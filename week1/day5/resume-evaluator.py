import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from pydantic import Field
from docx import Document

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY is missing from the workspace .env file.")

client = Groq(api_key = my_api_key)
model="openai/gpt-oss-20b"

job_description = """Job Title: Junior Python Backend Developer
Company: TechNova Solutions
Experience: 0-1 Years (Fresher)
Location: Pune, Maharashtra
Job Type: Full-Time
Job Description
We are looking for a motivated Junior Python Backend Developer to join our engineering team. The ideal candidate should have a good understanding of Python programming, Django, REST APIs, and database management.
Responsibilities
1. Develop and maintain backend applications using Python and Django.
2. Build and integrate RESTful APIs.
3. Work with PostgreSQL and MySQL databases.
4. Write clean, reusable, and maintainable code.
5. Debug and troubleshoot application issues.
6. Collaborate with frontend developers.
7. Participate in code reviews and team discussions.
Required Skills
- Python programming.
- Django / Django REST Framework.
- REST API development.
- PostgreSQL or MySQL.
- HTML, CSS, and JavaScript basics.
- Git and GitHub.
- Basic knowledge of Data Structures and Algorithms.
- Understanding of OOP concepts.
Good to Have
- Docker fundamentals.
- Redis and caching.
- Celery.
- AWS or cloud deployment.
- Basic understanding of CI/CD.
Eligibility
- BCA / BSc CS / BTech / MCA graduates.
- Freshers can apply.
- Good problem-solving and communication skills.
Salary
₹2.5 LPA – ₹4.5 LPA (Expected)
Interview Rounds
1. Aptitude Test
2. Python Technical Round
3. Backend Development Round
4. Practical Coding Assignment
5. HR Interview """

class JobD(BaseModel):
    
    role : str
    required_skills :list[str]
    preferred_skills :list[str]
    minimum_experiance : float | None
    educational_requirements : list[str]

jobd_schema = JobD.model_json_schema()

system_prompt = f"""
    you are an expert HR assistant.

    Your job is to analyze job description and extract structured information from them.
    return only validJSON matching this schema

    {jobd_schema}
    IMPORTANT:
    do not return the schema its self.
    do no return field like "properties" , "title" or "type.
    fil the schema with valid information extracted from job description.

    if minimun experiance is not mentioned , return null.
    if information for list is missing , return an empty list.
    Do not invent informaton .
"""
user_prompt = f"""
    analyze the following job description:
    {job_description}
"""

message_system={
    "role" : "system" ,
    "content" : system_prompt
} 
message_user={
    "role" : "user" ,
    "content" : user_prompt
} 

response_format = {
    "type" : "json_object"
}

messages = [message_system,message_user]
print(messages)
response = client.chat.completions.create(model = model , messages = messages , response_format=response_format)

answer = response.choices[0].message.content

role="user"



import json
row_json = answer
job_data = json.loads(row_json)
job = JobD(**job_data) 

print(job.minimum_experiance)
print(job.educational_requirements)

# part 2 -- parse real

class MatchResult(BaseModel):
    score : float
    details : dict

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

from pypdf import PdfReader
from docx import Document

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def read_docx(file_path):
    document = Document(file_path)
    text = ""
    for paragrapgh in document.paragraphs:
        
        if paragrapgh.text.strip():
            text += paragrapgh.text + "\n"

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:  # colunm ko cell kahete hai 
                if cell.text.strip():
                    text += cell.text + "\n"

    return text

def read_resume(file_path):
    if file_path.suffix.lower() == ".pdf":
        return read_pdf(file_path)
    elif file_path.suffix.lower() == ".docx":
        return read_docx(file_path)
    else:
        return None
    
def final_score(job, resume):
    match_schema = MatchResult.model_json_schema()
    prompt = f"""
    ypu are an HR recruiter.
    compare the candidates resume with the job description
    JOB DESCRIPTION:
    {job.model_dump_json(indent=2)}

    CANDIDATE RESUME:
    {resume.model_dump_json(indent=2)}
    Return JSON matching thid schema
    {match_schema}

    give me :
    1.candidate name
    2.matching skills
    3.missing important skills
    4.whether experiance requirements is met
    5.overall match percentage from 0 to 100 
    6.A short final verdict

    keep the response concise and easy to read
 
    """
    message={
        "role" : "user" ,
        "content" : prompt
    }

    messages = [message]
    response_format = {
        "type":"json_object"
    }
    response = client.chat.completions.create(model = model , messages = messages , response_format=response_format)
    data = json.loads(response.choices[0].message.content)
    return MatchResult(**data)



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

import time

resume_folder = Path("resumes")
all_results = []
for file_path in resume_folder.iterdir():
    if file_path.suffix.lower() not in [".pdf" , ".docx"]:
        continue
    print("\nProcessing:" , file_path.name)

    resume_text = read_resume(file_path)
    parsed_resume=parse_resume(resume_text)
    time.sleep(5)
    result = final_score(job , parsed_resume)
    time.sleep(5)
    print("Score:" , result.score)
    
    all_results.append({
        "name" : parsed_resume.name,
        "score" : result.score,
        "details" : result.details,
    })

all_results.sort(
    key=lambda candidate : candidate["score"],
    reverse = True
)

top_2 = all_results[:2]
worst_2 = all_results[-2:]

print("Top 2 candidates")
for candidate in top_2:
    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )
    print(candidate["details"])

print("LOWEST 2 CANDIDATES")
for candidate in worst_2:
    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )
    print(candidate["details"])