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

prompt="suggest name for a food company"
prompt1="hi"
prompt2="explain time travel in detail"
prompt3="write a SA on LLM in 1000 words"

prompts = [prompt, prompt1, prompt2, prompt3]

for prompt in prompts:
    message = {
    "role" : role ,
    "content" : prompt
    } 

    message_system={
    "role" : "system" ,
    "content" : "you are a brand manager who suggest name for my food startup . name should be in one word suggest one name only"
    }
    messages = [message_system,message]

    response = client.chat.completions.create(model = model , messages = messages , temperature=2 , max_tokens=50 )
    usage = response.usage
    print(f"Prompt: {prompt} your tokens:{usage.prompt_tokens} -->completion_tockens {usage.completion_tokens} , prompt_tokens {usage.prompt_tokens} , total_tokens {usage.total_tokens} , finish reason {response.choices[0].finish_reason} ")

# message_system={
#     "role" : "system" ,
#     "content" : "you are a brand manager who suggest name for my food startup . name should be in one word suggest one name only"
# }  

# message = {
#     "role" : role ,
#     "content" : prompt
# } 

# messages = [message_system,message]

# response = client.chat.completions.create(model = model , messages = messages , temperature=2  )
# print(response)

# print("############################")

# answer = response.choices[0].message.content
# print(answer) 