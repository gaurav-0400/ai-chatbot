import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field 
from groq import AsyncGroq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError ("GROQ_API_KEY is missing from the .env file")

client = AsyncGroq(api_key=api_key)

app= FastAPI(title= "AI Chatbot API")

class ChatRequest(BaseModel):
    message: str =Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    reply : str


@app.get("/")
def home():
    return {"message": "AI Chatbot API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request : ChatRequest):
    try:
        response= await client.chat.completions.create(
            # model="llama-3.3-70b-versatile",
            model="openai/gpt-oss-20b",
            messages= [
                {
                    "role" : "system",
                    "content" : (
                        "you are a helpful AI assistant."
                        "Answer clearly and accuratly"
                    ),
                },
                {
                    "role":"user",
                    "content": request.message,
                },
            ],
            temperature= 0.7,
        )
        answer = response.choices[0].message.content
        return ChatResponse(reply=answer or "")
    except Exception:
        import logging
        logging.exception("Groq API request failed")

        raise HTTPException(
            status_code= 502,
            detail= "Unable to generate the answer. Please try again later"
        )

