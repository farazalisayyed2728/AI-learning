import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY is missing from the workspace .env file.")

client = Groq(api_key = my_api_key)
model="openai/gpt-oss-20b"
role="user"

from pydantic import BaseModel
class Ticket(BaseModel):
    name : str
    email : str
    issue : str
schema = Ticket.model_json_schema()

response_format = {
    "type": "JSON_schema",

}


system_prompt = f"""
    Extract the personal information from the ticket strickly based on the schema and give me a JSON output
    {schema}"""

text = "hello i am a product buyer and its cant work properly please resolve the issue as soon as possible"

prompt=f""" 
this is a customer complaint message from a product buyer.
{text}
"""



message_system={
    "role" : "system" ,
    "content" : system_prompt
}  

message = {
    "role" : role ,
    "content" : prompt
} 

messages = [message_system,message]

response = client.chat.completions.create(model = model , messages = messages , response_format=response_format)
print(response)

print("############################")

answer = response.choices[0].message.content
print(answer) 