import os
import json
import time
from time import sleep
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from pydantic import Field
from docx import Document
from pypdf import PdfReader
from docx import Document

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

model="openai/gpt-oss-20b"

#step 1
knowledge_base = {
    "age" : " my name is faraz , The age of mine is 24 years",
    "net worth" : "Faraz net worth is 500000000",
    
}

#step 2 retrieval

def retiere_info(question):
    question=question.lower()
    if "age" in question:
        return knowledge_base["age"]

    elif "networth" in question:
        return knowledge_base["net worth"]
    else:
        return None

def ask_llm(question):
    context = retiere_info(question)
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
            model=model,
            messages=messages
        )
    answer=response.choices[0].message.content

    return answer


question = "what age ?"
print(ask_llm(question))