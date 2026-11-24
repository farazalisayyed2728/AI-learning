import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

import numpy as np
from sentence_transformers import SentenceTransformer\

model = SentenceTransformer("all-MiniLM-L6-v2")

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("GROQ_API_KEY is missing.")

client = Groq(api_key=my_api_key)
groqLLM = "openai/gpt-oss-20b"


documents = [
    "Employees receive 24 days of paid leave per year ." ,
    "employees work from the office on thusday , wedneday , thursday.",
    "monday friday are optional work from home days", 
    "employees recieve Rs 3000 per month for gym reimbursement " ,
    "employees canm claim Rs 2000 per month for home internet",
    "Employee have a 90 day notice period."
]

document_embeddings = model.encode(documents)
print(document_embeddings.size)

def cosine_similarity(a , b):
    return np.dot(a , b) /(
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def retrieve(qembedding):
    scores = []
    for i , document in enumerate(document_embeddings):
        score = cosine_similarity(qembedding , document)
        scores.append((score,documents[i]))

    scores.sort(reverse=True)
    return scores[0]



def ask_llm(question , context):
    sys_prompt = f"""answer in one sentence only, answer only based on this context. do not hallucinate {context}"""

    system_messages ={
        "role" : "system",
        "content" : sys_prompt
    }

    message={
        "role" : "user",
        "content" : question
    }

    messages = [system_messages ,message]


    response = client.chat.completions.create(
            model=groqLLM,
            messages=messages
        )
    answer=response.choices[0].message.content

    return answer


query = "how much vacation i get ?"
qembedding =  model.encode(query)

score,context = retrieve(qembedding)
answer = ask_llm(query, context)
print(answer)
# print(context) 