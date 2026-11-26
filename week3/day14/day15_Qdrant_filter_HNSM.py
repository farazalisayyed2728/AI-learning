import os 
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct ,Filter , FieldCondition , MatchValue , MatchAny , PayloadSchemaType
from sentence_transformers import SentenceTransformer
from groq import Groq
from qdrant_client.models import PayloadSchemaType
import json

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("GROQ_API_KEY is missing.")

QDRANT_URL= os.getenv("QDRANT_URL")
QDRANT_API_KEY= os.getenv("QDRANT_API_KEY")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing.")

groq_client = Groq(
    api_key=GROQ_API_KEY
)

client = QdrantClient(
    url = QDRANT_URL,
    api_key=QDRANT_API_KEY
    )

print("connected to qdrant cloud")


# part 3

COLLECTION_NAME = "knowledge_filter"
EMBEDDING_SIZE = 384


if client.collection_exists(COLLECTION_NAME):
    print("Collection already exists")
else:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_SIZE,
            distance=Distance.COSINE,
        ),
    )
    print("Collection created successfully")



print(f"Create collection: {COLLECTION_NAME}")
print(f"Vector size : {EMBEDDING_SIZE}")
print("Distance : COSINE")

client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="department",
    field_schema=PayloadSchemaType.KEYWORD
)

#part 4

with open("knowledge2.txt" , "r" , encoding="utf-8") as f:
    documents=json.load(f)

#part 5

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model ready")
texts = [document["text"] for document in documents]

embeddings = model.encode(texts)

print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding size : {EMBEDDING_SIZE}")


# part 6

points = []

for i, (document, embedding) in enumerate(zip(documents, embeddings)):
    point = PointStruct(
        id = i + 1,
        vector = embeddings[i].tolist(),
        payload={
            "text": document["text"],
            "category": document["category"],
            "is_active": document["is_active"]
            }
    )

    points.append(point)



# part 7

client.upsert(  #upload + insert
    collection_name = COLLECTION_NAME,
    points = points

)
print(f"Uploaded {len(points)} documents to Qdrant")


# part 8

def search(query, top_k=3):

    # Convert the question into an embedding
    query_vector = model.encode(query).tolist()

    # Search Qdrant for similar vectors
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    return results



def search_with_filter(query ,query_filter = None, top_k=3):

    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter = query_filter ,
    ).points

    return results

reimbursement_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="reimbursement")
        )
    ]
)


# part 9


query = "How many vacation days do I get?"

results = search(query, top_k=3)

print("\nSearch results:")

for result in results:
    print(f"Score: {result.score:.3f}")
    print(result.payload["text"])
    


# part 10


groq_client = Groq(
    api_key=GROQ_API_KEY
)

MODEL = "openai/gpt-oss-120b"


# part 11

def ask_llm(question, context):

    prompt = f"""
    Answer the question using only the information provided below.

    Context:
    {context}

    Question:
    {question}

    If the answer is not present in the context, say:
    "I don't know based on the provided information."
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# part 12

question = "How many vacation days do I get?"

# Step 1: Retrieve relevant documents from Qdrant
results = search(question, top_k=3)

# Step 2: Extract text from retrieved documents
context = "\n".join(
    result.payload["text"]
    for result in results
)

# Step 3: Send question + context to Groq
answer = ask_llm(question, context)

# Step 4: Display answer
print("\nFinal Answer:")
print(answer)