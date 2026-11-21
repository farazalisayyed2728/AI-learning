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

prompt="what is the capital of France?"

message = {
    "role" : "user",
    "content" : prompt
} 

messages = [message]

# response = client.chat.completions.create(model = model , messages = messages)
# print(response)

# # print("############################")

# answer = response.choices[0].message.content
# print(answer)


stream = client.chat.completions.create(model = model , messages = messages, stream=True)

for chunk in stream:
    content = chunk.choices[0].delta.content

    if content:
        print(content, end="", flush=True)