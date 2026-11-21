import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY is missing.")

client = Groq(api_key=my_api_key)

model = "openai/gpt-oss-20b"

prompt = "How does time work?"

message = {
    "role": "user",
    "content": prompt
}

messages = [message]

# Enable Streaming
response = client.chat.completions.create(
    model=model,
    messages=messages,
    stream=True
)

# Receive and print chunks
for chunk in response:
    content = chunk.choices[0].delta.content

    if content:
        print(content, end="", flush=True)