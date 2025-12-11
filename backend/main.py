
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
from tools.scraper import scrape_url, fetch_meta_image

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ContextIQ Backend")

# CORS Configuration
# Production Note: In real prod, replace ["*"] with specific domains e.g., ["https://myapp.com"]
origins = [
    "http://localhost:3000",  # React/Next.js default
    "http://localhost:5173",  # Vite default
    "http://localhost:8080",  # User specified frontend port
    "http://localhost:8000",  # Self
    "https://contextiq-seven.vercel.app", # Deployed Frontend
    "https://contextiq-seven.vercel.app/", 
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

from utils.session_manager import session_manager

@app.post("/agent/chat")
async def chat_endpoint(
    token_data: dict = Depends(verify_firebase_token),
    user_id: Optional[str] = Form(None), 
    session_id: Optional[str] = Form(None), # NEW: Accept session_id
    message: str = Form(None),
    context_link: str = Form(None),
    image: Union[UploadFile, str, None] = File(None)
):
    """
    Main Chat Endpoint (PROTECTED)
    """
    # Use UID from token as the source of truth
    current_user_id = token_data.get("uid")
    
    if not current_user_id and user_id:
        current_user_id = user_id
    
    # Session Management Logic
    if not session_id or session_id == "undefined":
        # Create a new session if none provided
        session_id = session_manager.create_session(current_user_id)
        
    session_data = session_manager.load_session(session_id)
    
    if not session_data:
        # Create new session if invalid ID
        session_id = session_manager.create_session(current_user_id, session_id)
        session_data = session_manager.load_session(session_id)
    
    # Check ownership and transfer if needed (Guest -> Real User)
    if session_data.get("user_id") in ["guest_user", "unknown", None] and current_user_id and current_user_id != "guest_user":
        print(f"🔄 Transferring session {session_id} to user {current_user_id}")
        session_manager.transfer_session(session_id, current_user_id)
        # Update local ref
        session_data["user_id"] = current_user_id
        
    history = session_data["history"]

    # Construct input parts
    input_parts = []
    
    text_prompt = ""
    if message:
        text_prompt += f"User Message: {message}\n"
        
        # Automatic Link Extraction and Scraping
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
        text_prompt += f"\n--- EXPLICIT CONTEXT LINK ---\nSource: {context_link}\n"
        try:
             scraped_content = scrape_url(context_link)
             text_prompt += f"{scraped_content}\n"
        except Exception as e:
             text_prompt += f"Error reading link: {e}\n"

    if text_prompt:
        input_parts.append(text_prompt)
        
    if image:
        if isinstance(image, UploadFile):
            try:
                contents = await image.read()
                img = Image.open(io.BytesIO(contents))
                input_parts.append(img)
                input_parts.append("\n[Using the attached image as visual context]\n")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")
        elif isinstance(image, str):
            print(f"⚠️ Received string for image field, ignoring: {image}")
    
    if not input_parts:
        raise HTTPException(status_code=400, detail="No input provided (text, link, or image required)")

    # Run Agent
    try:
        response = agent.run(input=input_parts, chat_history=history)
        
        # Save updated history
        session_manager.save_session(session_id, response.chat_history)
        
        # Parse Structured JSON Output
        # import json # Already imported at top-level ideally, but local import is fine if kept
        raw_output = response.output
        
        final_response = {
            "agent_response": raw_output,
            "session_id": session_id,
            "products": []
        }

        try:
            # Try to clean markdown code blocks first
            clean_json = raw_output.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(clean_json)
        except json.JSONDecodeError:
            # Fallback: Try to find start and end of JSON using Regex
            try:
                # import re # Removed to avoid UnboundLocalError
                match = re.search(r'\{.*\}', raw_output, re.DOTALL)
                if match:
                   json_str = match.group(0)
                   parsed_data = json.loads(json_str)
                else:
                   raise ValueError("No JSON found")
            except Exception:
                # If all parsing fails, keep the raw output as the message
                parsed_data = None

        if isinstance(parsed_data, dict):
            final_response["agent_response"] = parsed_data.get("agent_response", raw_output)
            final_response["products"] = parsed_data.get("products", [])
            final_response["predictive_insight"] = parsed_data.get("predictive_insight", None)
            final_response["session_id"] = parsed_data.get("session_id", session_id) # Trust model if it returns session_id? No, sticky to verified.
            
            # Ensure products is a list and populate images if missing
            if isinstance(final_response["products"], list):
                for product in final_response["products"]:
                    if isinstance(product, dict) and product.get("link"):
                        if not product.get("image") or product.get("image") == "No Image":
                            print(f"🖼 Fetching image for {product['link']}...")
                            img_url = fetch_meta_image(product['link'])
                            if img_url:
                                product["image"] = img_url
                                print(f"✅ Found image: {img_url}")
                            else:
                                print(f"❌ No image found for {product['link']}")
            else:
                 final_response["products"] = []
        
        return final_response
        
    except Exception as e:
        print(f"❌ Critical Endpoint Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/history")
async def get_history(token_data: dict = Depends(verify_firebase_token)):
    user_id = token_data.get("uid")
    sessions = session_manager.list_user_sessions(user_id)
    print(f"📂 History request for user: {user_id}. Found {len(sessions)} sessions.")
    return sessions

@app.get("/agent/session/{session_id}")
async def get_session_details(session_id: str, token_data: dict = Depends(verify_firebase_token)):
    """Fetch messages for a specific session."""
    user_id = token_data.get("uid")
    data = session_manager.load_session(session_id)
    
    if not data or data.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = []
    for msg in data["history"]:
        role = "user" if msg.role == "user" else "assistant"
        content = msg.parts[0].text if msg.parts else ""
        messages.append({"role": role, "content": content})
        
    return {"title": data.get("title"), "messages": messages}

class TitleRequest(BaseModel):
    session_id: str

@app.post("/agent/title")
async def generate_title(req: TitleRequest, token_data: dict = Depends(verify_firebase_token)):
    """Generate a title for the session based on context."""
    user_id = token_data.get("uid")
    data = session_manager.load_session(req.session_id)
    
    if not data or data.get("user_id") != user_id:
         raise HTTPException(status_code=404, detail="Session not found")
         
    history = data["history"]
    if not history:
        return {"title": "New Chat"}
    
    # Generate title using Gemin (lightweight logic)
    # Simple heuristic: First 3-4 words of first user message
    first_msg = None
    for msg in history:
        if msg.role == "user":
            first_msg = msg.parts[0].text
            break
            
    if not first_msg:
        return {"title": "New Chat"}
        
    # Remove common start phrases
    clean_msg = first_msg.lower()
    prefixes = ["help me find", "show me", "i want to buy", "looking for", "search for"]
    for p in prefixes:
        if clean_msg.startswith(p):
            clean_msg = clean_msg[len(p):].strip()
            break
            
    # Take first 4 words
    words = clean_msg.split()[:4]
    title = " ".join(words).title()
    
    # SAVE THE TITLE
    session_manager.save_session(req.session_id, history, title=title)
    
    return {"title": title}


@app.get("/health")
def health_check():
    return {"status": "ContextIQ is Online"}

@app.on_event("startup")
async def startup_event():
    print("Starting ContextIQ Backend...")