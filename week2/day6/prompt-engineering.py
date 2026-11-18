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

def llm_ans(prompt):
    message = {
        "role" : "user",
        "content" : prompt
    }

    messages = [message]
    response = client.chat.completions.create(model = model , messages = messages)
    ans = response.choices[0].message.content
    return ans

bad_prompt = """
#ROLE :
you are a support assistant at laptop company.

#TASK:
You have to classify the issue in a category.

#CONSTRAINTS :
you have to classify the issue in one of the 3 category mainly Billing , Technical issue , Return.

#OUTPUT FORMAT :
your answer should be in the one word only . The one word should be one of the categories given constraints.

#EXAMPLE :
for instance if a user compalin says he want a refund then the category is Return.

#FALLBACK :
if the issue is unrelated to any of the category mentioned in the constraint , then the answer should be OTHER .

This is a user complaint:
my laptop is not working .
"""


print(llm_ans(bad_prompt))