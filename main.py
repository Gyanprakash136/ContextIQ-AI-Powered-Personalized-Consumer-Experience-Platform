
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from core.agent_builder import build_contextiq_agent
import shutil
import os
import json
import pickle
from typing import List, Optional, Union
from PIL import Image
import io
import re
from tools.scraper import scrape_url

app = FastAPI(title="ContextIQ Backend")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"❌ Validation Error: {exc.errors()}")
    try:
        body = await request.body()
        body_str = body.decode('utf-8', errors='ignore')[:1000]
    except Exception:
        body_str = "Body could not be read (stream consumed)"
        
    print(f"📩 Request Body: {body_str}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body_str},
    )

# Ensure sessions directory exists
os.makedirs("sessions", exist_ok=True)

# Initialize Agent
agent = build_contextiq_agent()

def load_history(user_id: str):
    """Load chat history from local file storage."""
    path = f"sessions/{user_id}.pkl"
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return []
    return []

def save_history(user_id: str, history):
    """Save chat history to local file storage."""
    path = f"sessions/{user_id}.pkl"
    with open(path, "wb") as f:
        pickle.dump(history, f)

@app.post("/agent/chat")
async def chat_endpoint(
    user_id: str = Form(...),
    message: str = Form(None),
    context_link: str = Form(None),
    image: Union[UploadFile, str, None] = File(None)
):
    """
    Main Chat Endpoint supporting Text + Link + Image
    """
    history = load_history(user_id)
    
    # Construct input parts
    input_parts = []
    
    text_prompt = ""
    if message:
        text_prompt += f"User Message: {message}\n"
        
        # Automatic Link Extraction and Scraping
        # Find all http/https links
        urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', message)
        if urls:
            print(f"🔗 Detected URLs: {urls}")
            text_prompt += "\n--- SCRAPED CONTENT ---\n"
            for url in urls:
                try:
                    text_prompt += f"\nSOURCE: {url}\n"
                    scraped_content = scrape_url(url)
                    text_prompt += f"CONTENT:\n{scraped_content}\n"
                except Exception as e:
                    text_prompt += f"Error scraping {url}: {e}\n"
            text_prompt += "\n--- END SCRAPED CONTENT ---\n"

    # Deprecated: context_link (keeping for backward compatibility but optional)
    if context_link:
        # If the user explicitly provided a link via the form field, scrape it too
        text_prompt += f"\n--- EXPLICIT CONTEXT LINK ---\nSource: {context_link}\n"
        try:
             scraped_content = scrape_url(context_link)
             text_prompt += f"{scraped_content}\n"
        except Exception as e:
             text_prompt += f"Error reading link: {e}\n"

    if text_prompt:
        input_parts.append(text_prompt)
        
    if image:
        # Check if it's actually an UploadFile (ignore strings)
        if isinstance(image, UploadFile):
            try:
                # Read image into PIL
                contents = await image.read()
                img = Image.open(io.BytesIO(contents))
                input_parts.append(img)
                input_parts.append("\n[Using the attached image as visual context]\n")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")
        elif isinstance(image, str):
            # If it's a string, likely empty or invalid upload, just ignore or log
            print(f"⚠️ Received string for image field, ignoring: {image}")
    
    if not input_parts:
        raise HTTPException(status_code=400, detail="No input provided (text, link, or image required)")

    # Run Agent
    try:
        response = agent.run(input=input_parts, chat_history=history)
        
        # Save updated history
        save_history(user_id, response.chat_history)
        
        # Check if we have structured output or just text
        # For this hackathon MVP, we return the text and maybe parse it if needed
        # The TDD asks for specific JSON fields (agent_response, products, etc.)
        # We can ask the agent to return JSON or parse the text.
        # For now, we return the raw text, but wrapped in the requested format.
        
        return {
            "agent_response": response.output,
            "session_id": user_id,
            # In a full implementation, we would extract specific product data here
            # "products": [], 
            # "predictive_insight": ...
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ContextIQ is Online"}

@app.on_event("startup")
async def startup_event():
    print("Starting ContextIQ Backend...")