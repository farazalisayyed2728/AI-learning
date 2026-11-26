import os 
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from groq import Groq

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

# groqLLM = "openai/gpt-oss-20b"

COLLECTION_NAME = "knowledge"
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

with open("knowledge.txt" , "r" , encoding="utf-8") as f:
    documents = [
        line.strip()
        for line in f
        if line.strip()
    ]

print(f"loaded {len(documents)} documents")



print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model ready")
embeddings = model.encode(documents)

print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding size : {EMBEDDING_SIZE}")



points = []

for i , embedding in enumerate(embeddings):
    point = PointStruct(
        id = i + 1,

        vector = embedding.tolist(),

        payload = {
            "text" : documents[i]
        }
    )

    points.append(point)


client.upsert(  #upload + insert
    collection_name = COLLECTION_NAME,
    points = points

)
print(f"Uploaded {len(points)} documents to Qdrant")



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


query = "How many vacation days do I get?"

results = search(query, top_k=3)

print("\nSearch results:")

for result in results:
    print(f"Score: {result.score:.3f}")
    print(result.payload["text"])
    print()




groq_client = Groq(
    api_key=GROQ_API_KEY
)

MODEL = "openai/gpt-oss-120b"


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
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content



# ==========================================
# PART 12 - COMPLETE RAG PIPELINE
# ==========================================

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