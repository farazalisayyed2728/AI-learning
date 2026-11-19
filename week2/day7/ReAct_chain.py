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

#TOOLS - api banana abhi sirf general function bana rahe hai 

def get_product_price(product):
    if product == 'iphone 17':
        return 1000
    elif product == 'iphone 15':
        return 500
    else:
        return 0

def calculator(expression):
    try:
        return eval(expression)  #inbuilt function jisme expression milta hai or wwo eval uate karta hai 
    except:
        return "calc error"

tools = {
    "get_product_price" : get_product_price,
    "calculator" : calculator
}


system_prompt = """
You are a shopping assistant.
you have these tools :
get_product_price(expression)
calculator(expression)

IMPORTANT:
Call tools exactly like these example :

Action: get_product_price("iphone 17")
Action: calculator("5000 - 1000")

Never write :
get_product_price(product = "iphone 17")

Never write :
calculator(expression = "5000 - 1000")

Follow these rules :

1 . Decide what you need to do next.
2. call only one tool at time .
3. after writing action stop immidiately.
4. Never guess or invent a tool result.
5. then decide your next action.
7. when the task is complete , give the final answer.

Format exactly like this, without markdown:
Thought: what you need to do
Action: tool_name(argument)

When finished:
Final Answer: your answer

"""

def run_agent(question):
    messages = [
        {   "role" : "system",
            "content" : system_prompt
        }, 
        {
            "role" : "user",
            "content" : question
        }
    ]

    for step in range(5):
        print("\n-------------------")
        print("STEP" , step + 1)
        print("---------------------")

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0
        )

        answer = response.choices[0].message.content
        print(answer)

        #agent has finished

        if re.search(r"Final\s+Answer\s*:", answer, re.IGNORECASE):
            break

        # Find the Action
        match = re.search(
            r"Action\s*:\s*(\w+)\s*\((.*?)\)",
            answer,
            re.IGNORECASE
        )

        if match:
            tool_name = match.group(1)

            tool_input = match.group(2)

            tool_input = tool_input.strip()

            tool_input = tool_input.strip('"')
            
            # Run the tool
            if tool_name in tools:
                tool = tools[tool_name]

                observation = tool(tool_input)

            else:
                observation = "Tool not found"

            print("Observation:", observation)
            # add LLM response to memory
            messages.append({
                            "role" : "assistant",
                            "content" : answer
                            
            })

            # give tools result back to LLM
            messages.append({
                "role" : "user",
                "content" :
                        "Observation: " +
                            str(observation)
            })
            sleep(5)
        else:
            raise RuntimeError(
                "The assistant response contained neither an action nor a final answer."
            )

prompt = """
I have 5000 rupees. what is the price of an iphone 17?
and how much money will i have left ? 
"""
run_agent(prompt)