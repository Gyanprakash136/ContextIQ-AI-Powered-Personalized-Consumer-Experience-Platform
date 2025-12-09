
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from core.agent_builder import build_contextiq_agent
import shutil
import os
import json
import pickle
from typing import List, Optional
from PIL import Image
import io

app = FastAPI(title="ContextIQ Backend")

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
    image: UploadFile = File(None)
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
        
    if context_link:
        text_prompt += f"\nCONTEXT LINK: {context_link}\n(Please use the scraper tool to read this)\n"
        
    if text_prompt:
        input_parts.append(text_prompt)
        
    if image:
        try:
            # Read image into PIL
            contents = await image.read()
            img = Image.open(io.BytesIO(contents))
            input_parts.append(img)
            input_parts.append("\n[Using the attached image as visual context]\n")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

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