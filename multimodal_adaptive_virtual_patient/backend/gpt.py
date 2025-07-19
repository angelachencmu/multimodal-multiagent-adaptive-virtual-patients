import copy
from uuid import uuid4
import openai
from dotenv import load_dotenv
import os

load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

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

def getGPTEmbedding(text):
    response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
    embedding = response.data[0].embedding
    return embedding

def getGPTtts(text, voice, instructions):
    try:
        filename = f"{uuid4().hex}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions=instructions,
        ) as response:
            response.stream_to_file(filepath)
        
        return f"/audio/{filename}"

    except Exception as e:
        print(f"Error generating audio: {e}")
        return None