import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field 
from groq import AsyncGroq

from fastapi.middleware.cors import CORSMiddleware
from typing import Literal #####


load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError ("GROQ_API_KEY is missing from the .env file")

client = AsyncGroq(api_key=api_key)

# app= FastAPI(title= "AI Chatbot API")

app = FastAPI(title="AI Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "https://ai-chatbot-frontend-kxlg.onrender.com"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# class ChatRequest(BaseModel):
#     message: str =Field(min_length=1, max_length=4000)

###TO store the history and send into the API 
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)



class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[Message] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    reply : str


@app.get("/")
def home():
    return {"message": "AI Chatbot API is running"}

# @app.post("/chat", response_model=ChatResponse)
# async def chat(request : ChatRequest):
#     try:
#         response= await client.chat.completions.create(
#             # model="llama-3.3-70b-versatile",
#             model="openai/gpt-oss-20b",
#             messages= [
#                 {
#                     "role" : "system",
#                     "content" : (
#                         "you are a helpful AI assistant."
#                         "Answer clearly and accuratly"
#                     ),
#                 },
#                 {
#                     "role":"user",
#                     "content": request.message,
#                 },
#             ],
#             temperature= 0.7,
#         )
#         answer = response.choices[0].message.content


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        messages = [
            {
                "role": "system",
                # "content": (
                #     "You are a helpful AI assistant. "
                #     "Answer clearly and accurately. "
                #     "Use the conversation history to understand "
                #     "follow-up questions."
                "content": (
                    "You are a helpful, professional AI assistant.\n\n"
                    "Response guidelines:\n"
                    "1. Answer the user's question directly and accurately.\n"
                    "2. Use clear, simple language that is easy to understand.\n"
                    "3. Format responses using Markdown when appropriate.\n"
                    "4. Use short headings to organize longer answers.\n"
                    "5. Use bullet points for lists and numbered steps for procedures.\n"
                    "6. Put programming code inside properly labeled code blocks.\n"
                    "7. Use tables only when they make comparisons easier to understand.\n"
                    "8. Give practical examples when they help explain a concept.\n"
                    "9. Keep simple answers short. Provide detailed explanations only when needed.\n"
                    "10. For follow-up questions, use the conversation history to understand the context.\n"
                    "11. If the question is unclear, ask a brief clarifying question.\n"
                    "12. Do not add unnecessary introductions, repeated conclusions, or irrelevant information.\n"
                    "13. Never invent facts. Clearly state when you are uncertain.\n"
                    "14. Do not use Markdown formatting excessively; keep responses clean and readable."
                    "15. For educational or technical answers, use this structure when appropriate: "
                    "brief definition, explanation, example, and key takeaway. "
                    "Use Markdown headings, lists, and code blocks only when useful.\n"
                ),
                
            }
        ]

        # Include previous conversation messages
        messages.extend(
            item.model_dump() for item in request.history
        )

        # Add the current question
        messages.append({
            "role" :"user",
            "content": request.message,
        })

        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.7,
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

