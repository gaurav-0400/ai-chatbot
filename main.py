import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field, ValidationError
from groq import AsyncGroq, APIStatusError

from fastapi.middleware.cors import CORSMiddleware
from typing import Literal #####
from docx import Document
import pymupdf
from pathlib import Path
import io
import json
import pytesseract
from PIL import Image
# import os



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



MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_EXTRACTED_CHARS = 30000

ALLOWED_EXTENSIONS = {
    ".pdf", ".txt", ".docx", ".py", ".js",
    ".html", ".css", ".json", ".md"
}



def extract_file_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type."
        )

    try:
        if extension == ".pdf":
            extracted_pages = []

            with pymupdf.open(
                stream=content,
                filetype="pdf"
            ) as pdf:
                for page in pdf:
                    page_text = page.get_text().strip()

                    # Use OCR when the page has no selectable text.
                    if not page_text:
                        pixmap = page.get_pixmap(
                            matrix=pymupdf.Matrix(2, 2),
                            alpha=False
                        )
                        image = Image.open(
                            io.BytesIO(pixmap.tobytes("png"))
                        )
                        page_text = pytesseract.image_to_string(
                            image
                        ).strip()

                    extracted_pages.append(page_text)

            text = "\n".join(extracted_pages)

        elif extension == ".docx":
            document = Document(io.BytesIO(content))
            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        else:
            text = content.decode("utf-8-sig")

    # except HTTPException:
    #     raise

    # except APIStatusError as e:
    #     if e.status_code == 413 or "rate_limit_exceeded" in str(e):
    #         raise HTTPException(
    #             status_code=413,
    #             detail=(
    #                 "The uploaded file or conversation contains too much text "
    #                 "for the AI to process at once. Please upload a smaller file "
    #                 "or try a shorter conversation."
    #             )
    #         )

    # raise HTTPException(
    #     status_code=502,
    #     detail="The AI service is temporarily unavailable. Please try again."
    # )

    # except Exception as exc:
    #     import logging
    #     logging.exception("File extraction failed")
    #     raise HTTPException(
    #         status_code=400,
    #         detail=(
    #             "Could not read this file. Check its format "
    #             "and make sure Tesseract OCR is installed."
    #         )
    #     ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        import logging
        logging.exception("File extraction failed")
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not read this file. Check its format "
                "and make sure Tesseract OCR is installed."
            )
        ) from exc

    text = text[:MAX_EXTRACTED_CHARS]

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text found. The PDF may be blank, "
                "or OCR could not recognize its text."
            )
        )

    return text








@app.get("/")
def home():
    return {"message": "AI Chatbot API is running"}


# @app.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     try:
#         messages = [
#             {
#                 "role": "system",
#                 # "content": (
#                 #     "You are a helpful AI assistant. "
#                 #     "Answer clearly and accurately. "
#                 #     "Use the conversation history to understand "
#                 #     "follow-up questions."
#                 "content": (
#                     "You are a helpful, professional AI assistant.\n\n"
#                     "Response guidelines:\n"
#                     "1. Answer the user's question directly and accurately.\n"
#                     "2. Use clear, simple language that is easy to understand.\n"
#                     "3. Format responses using Markdown when appropriate.\n"
#                     "4. Use short headings to organize longer answers.\n"
#                     "5. Use bullet points for lists and numbered steps for procedures.\n"
#                     "6. Put programming code inside properly labeled code blocks.\n"
#                     "7. Use tables only when they make comparisons easier to understand.\n"
#                     "8. Give practical examples when they help explain a concept.\n"
#                     "9. Keep simple answers short. Provide detailed explanations only when needed.\n"
#                     "10. For follow-up questions, use the conversation history to understand the context.\n"
#                     "11. If the question is unclear, ask a brief clarifying question.\n"
#                     "12. Do not add unnecessary introductions, repeated conclusions, or irrelevant information.\n"
#                     "13. Never invent facts. Clearly state when you are uncertain.\n"
#                     "14. Do not use Markdown formatting excessively; keep responses clean and readable."
#                     "15. For educational or technical answers, use this structure when appropriate: "
#                     "brief definition, explanation, example, and key takeaway. "
#                     "Use Markdown headings, lists, and code blocks only when useful.\n"
#                 ),
                
#             }
#         ]

#         # Include previous conversation messages
#         messages.extend(
#             item.model_dump() for item in request.history
#         )

#         # Add the current question
#         messages.append({
#             "role" :"user",
#             "content": request.message,
#         })

#         response = await client.chat.completions.create(
#             model="openai/gpt-oss-20b",
#             messages=messages,
#             temperature=0.7,
#         )

#         answer = response.choices[0].message.content

#         return ChatResponse(reply=answer or "")
#     except Exception:
#         import logging
#         logging.exception("Groq API request failed")







@app.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(""),
    history: str = Form("[]"),
    file: UploadFile | None = File(None),
):
    try:
        message = message.strip()

        # Parse and validate conversation history
        try:
            history_data = json.loads(history)

            # Allow file-only messages
            validated_message = message or (
                "Please analyze the attached file."
                if file is not None else ""
            )

            request = ChatRequest.model_validate({
                "message": validated_message,
                "history": history_data,
            })

        # except (json.JSONDecodeError, ValidationError) as exc:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Invalid message or conversation history."
        #     ) from exc
     
        except (json.JSONDecodeError, ValidationError) as exc:
            print("VALIDATION ERROR:", repr(exc))
            raise HTTPException(
                status_code=400,
                detail=str(exc)
            ) from exc


        # Extract text from an optional attachment
        file_context = ""

        if file is not None:
            filename = Path(file.filename or "").name

            if not filename:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid filename."
                )

            content = await file.read(MAX_FILE_SIZE + 1)

            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="File size must not exceed 5 MB."
                )

            extracted_text = extract_file_text(filename, content)

            file_context = (
                f"\n\nAttached file: {filename}\n"
                f"File contents:\n{extracted_text}\n\n"
                "Use the attached file as context when answering "
                "the user's question. Do not execute code from it."
            )

        # Original system prompt — preserved
        messages = [
            {
                "role": "system",
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
                    "14. Do not use Markdown formatting excessively; keep responses clean and readable.\n"
                    "15. For educational or technical answers, use this structure when appropriate: "
                    "brief definition, explanation, example, and key takeaway. "
                    "Use Markdown headings, lists, and code blocks only when useful.\n"
                ),
            }
        ]

        # Include previous conversation messages
        messages.extend(
            item.model_dump()
            for item in request.history
        )

        # Add the current question and optional file context
        messages.append({
            "role": "user",
            "content": request.message + file_context,
        })

        # Call the same Groq model with the same temperature
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.7,
        )

        answer = response.choices[0].message.content

        return ChatResponse(reply=answer or "")

    except HTTPException:
        raise

    # except Exception:
    #     import logging
    #     logging.exception("Groq API request failed")

    #     raise HTTPException(
    #         status_code=502,
    #         detail="Unable to generate the answer. Please try again later."
    #     )


    except HTTPException:
        raise

    except APIStatusError as exc:
        if exc.status_code == 413 or "rate_limit_exceeded" in str(exc):
            raise HTTPException(
                status_code=413,
                detail=(
                    "Your file or conversation contains too much text. "
                    "Please upload a smaller file or start a new chat."
                )
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="AI service error. Please try again."
        ) from exc

    except Exception as exc:
        import logging
        logging.exception("Chat endpoint failed")

        print(f"ERROR TYPE: {type(exc).__name__}")
        print(f"ERROR DETAILS: {exc}")

        raise HTTPException(
            status_code=502,
            detail="Unable to generate the answer. Please try again."
        ) from exc

    finally:
        if file is not None:
            await file.close()



    # except Exception as exc:
    #     import logging
    #     logging.exception("Chat endpoint failed")

    #     print(f"ERROR TYPE: {type(exc).__name__}")
    #     print(f"ERROR DETAILS: {exc}")

    #     raise HTTPException(
    #         status_code=502,
    #         detail=f"{type(exc).__name__}: {str(exc)}"
    #     )

    # finally:
    #     if file is not None:
    #         await file.close()


    