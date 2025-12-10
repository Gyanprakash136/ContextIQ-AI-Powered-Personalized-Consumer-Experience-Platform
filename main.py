
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends
from core.auth import verify_firebase_token
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

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ContextIQ Backend")

# CORS Configuration
# Production Note: In real prod, replace ["*"] with specific domains e.g., ["https://myapp.com"]
origins = [
    "http://localhost:3000",  # React/Next.js default
    "http://localhost:5173",  # Vite default
    "http://localhost:8080",  # User specified frontend port
    "http://localhost:8000",  # Self
    "*"                       # Allow all for hackathon flexibility
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Allow Authorization, Content-Type, etc.
)

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

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends
from core.auth import verify_firebase_token
import shutil

# ... existing imports ...

# ... existing code ...

@app.post("/agent/chat")
async def chat_endpoint(
    # Auth Dependency: Validates header "Authorization: Bearer <token>"
    token_data: dict = Depends(verify_firebase_token),
    # user_id form field is now OPTIONAL or ignored in favor of token
    user_id: Optional[str] = Form(None), 
    message: str = Form(None),
    context_link: str = Form(None),
    image: Union[UploadFile, str, None] = File(None)
):
    """
    Main Chat Endpoint (PROTECTED)
    """
    # Use UID from token as the source of truth
    current_user_id = token_data.get("uid")
    
    # Fallback to form user_id ONLY if allowed (mock mode) or for migration
    # ideally we force token uid
    if not current_user_id and user_id:
        current_user_id = user_id
    
    # Use current_user_id for logic
    history = load_history(current_user_id)

    
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
        save_history(current_user_id, response.chat_history)
        
        # Parse Structured JSON Output
        import json
        raw_output = response.output
        
        # Default fallback
        final_response = {
            "agent_response": raw_output,
            "session_id": current_user_id,
            "products": []
        }

        try:
            # Clean potential markdown wrapping ```json ... ```
            clean_json = raw_output.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(clean_json)
            
            # If successful, merge into final response
            if isinstance(parsed_data, dict):
                final_response["agent_response"] = parsed_data.get("agent_response", raw_output)
                final_response["products"] = parsed_data.get("products", [])
                final_response["predictive_insight"] = parsed_data.get("predictive_insight", None)
                
        except json.JSONDecodeError:
            print("⚠️ Agent returned non-JSON text. Falling back to raw output.")
            pass
        
        return final_response
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ContextIQ is Online"}

@app.on_event("startup")
async def startup_event():
    print("Starting ContextIQ Backend...")