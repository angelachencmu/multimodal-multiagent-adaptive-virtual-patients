import copy
import openai
from dotenv import load_dotenv
import os

load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def queryGPT(messages, message="return failed"):
    local_messages = copy.deepcopy(messages)
    local_messages.append({"role": "user", "content": message})

    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=local_messages
    )

    reply = chat.choices[0].message.content
    local_messages.append({"role": "assistant", "content": reply})

    return reply, local_messages