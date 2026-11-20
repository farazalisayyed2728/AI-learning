import os
import re
from pathlib import Path
from time import sleep

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
from docx import Document

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY is missing from the workspace .env file.")

client = Groq(api_key = my_api_key)
model="openai/gpt-oss-20b"

JD = """
We are hiring a Backend python Developer.
- Strong python 
- FastApi or Django 
- PostgreSQL
- Docker
- AWS
- Rest APIS
- 2+ years of experience
"""

RESUME = """
Name : rahul sharma 

experience : 2 years as a software engineer.

Skills : python, FastApi, Django, PostgreSQL, Docker, AWS, Rest APIs

projects :
- Developed a web application using FastApi and PostgreSQL.

deploy application on AWS using Docker.
"""


def ask_llm(system_prompt , user_prompt):
    sys_msg = {
        "role": "system",
        "content": system_prompt

    }
    user_msg = {
        "role": "user",
        "content": user_prompt
    }

    messages = [sys_msg, user_msg]

    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


def step1_resume_extractor(RESUME):
    print("----------STEP 1----------")
    #extract skill from resume 
    system_prompt = """You are a resume extractor. You will be given a resume and you need to extract the skills from it. only retrn the skills no other informations . Do not invent any skill by yourself """
    user_prompt = f"""
    extract the skills from the following resume and return them as a list of skills.
    {RESUME}
    """
    return ask_llm(system_prompt, user_prompt)

def step2_JD_extractor(JD):
    print("----------STEP 2----------")
    #extract skill from JD
    system_prompt ="""You are a resume extractor. You will be given a resume and you need to extract the skills from Job Description provided. only retrn the skills no other informations . Do not invent any skill by yourself .

    Output Format :
    Skills should be separated by comma. just return comma separated skills do not return any other filler information.
    
    """

    user_prompt = f"""
    extract the skills from this JD.
    {JD}
    """
    return ask_llm(system_prompt, user_prompt)

def step3_matcher(candidate, jd):
    print("----------STEP 3----------")

    system_prompt = """You are a professional HR assistant. compare the skills and candidate and the skills required in the JD and produce a final score between 1 and 100 .  also produce a short verdict wheather the cancidate is a good fit for the role """
    
    user_prompt =f"""
    compare and match skills .
    JD:
    {jd}
    Candidate :
    {candidate}

    """
    return ask_llm(system_prompt, user_prompt)


candidate=step1_resume_extractor(RESUME)
print(candidate)
sleep(2)

jd= step2_JD_extractor(JD)
print(jd)
sleep(2)

score = step3_matcher(candidate, jd)
print(score)