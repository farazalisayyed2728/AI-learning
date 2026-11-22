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

api = FastAPI()

class experience(BaseModel):
    company : str | None = None
    role : str | None = None
    duration : str | None = None
    description : str | None = None
    skills_used : list[str] = []

class Resume(BaseModel):
    name : str | None = None
    email: str | None = None
    phone : str | None = None

    total_experiance_years :float |None = None
    skills : list[str]
    experiences: list[experience] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    project : list[str] = []
    certification : list[str] = []

resume_schema = Resume.model_json_schema()

class ChatRequest(BaseModel):
    question : str

def ask_candidante(question: str, resume: Resume):
    system_prompt = f"""
    You are an expert AI resume evaluator.

    Evaluate the candidate based on the resume and answer the question.

    Resume:
    {resume.model_dump_json(indent=2)}

Rules:
1. Answer the question based on the information provided in the resume.
2.never hallucinate
3.if information is unavailable , say

"i dont have enough information to answer that."

4. be professional.
5. Answer as if HR is interviewing this candidate.

    """

    user_prompt = f"""
    Question: {question}
    """

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    answer = response.choices[0].message.content

    return answer


class ChatResponse(BaseModel):
    answer : str


#parsing resume 
def parse_resume(resume_text):

    system_prompt = f"""
    You are an expert AI resume parser.

    Extract candidate information from the resume.

    Return only valid JSON matching this schema:
    {resume_schema}

    Never invent information.
    Return null for missing values.
    """

    user_prompt = f"""
    Parse the following resume:
    {resume_text}
    """

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
        
    )

    answer = response.choices[0].message.content

    return Resume(**json.loads(answer))

#pdf extraction
def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

@api.get("/")
def home():
    resume_path = Path(__file__).resolve().parent / "Faraz_Ali_Resume_1.pdf"
    resume_text = read_pdf(resume_path)

    resume = parse_resume(resume_text)
    print(resume.model_dump_json(indent=4))

    return {
        "message":"This is a home page."
    }

@api.post("/chat")
def chat(request : ChatRequest):
    resume_path = Path(__file__).resolve().parent / "Faraz_Ali_Resume_1.pdf"
    resume_text = read_pdf(resume_path)
    resume = parse_resume(resume_text)
    answer = ask_candidante(request.question, resume)
    return {
        "answer" : answer
    }

app = CORSMiddleware(
    app=api,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)