from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from core.auth import verify_firebase_token
from core.agent_builder import build_fast_agent, build_heavy_agent
from core.router import classify_intent
from utils.session_manager import session_manager
import json
import re

app = FastAPI(title="ContextIQ Backend")

# CORS (Keep your existing settings)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents ONCE
print("🚀 Initializing Agents...")
FAST_AGENT = build_fast_agent()
HEAVY_AGENT = build_heavy_agent()
print("✅ Agents Ready")

@app.post("/agent/chat")
async def chat_endpoint(
    token_data: dict = Depends(verify_firebase_token),
    message: str = Form(...),
    session_id: str = Form(None),
    image: UploadFile = File(None)
):
    user_id = token_data.get("uid")
    
    # 1. Manage Session
    if not session_id or session_id == "undefined":
        session_id = session_manager.create_session(user_id)
        
    session_data = session_manager.load_session(session_id)
    if not session_data:
        # Create new session if invalid ID provided
        session_id = session_manager.create_session(user_id)
        session_data = session_manager.load_session(session_id)
        
    history = session_data["history"]

    # 2. Route Intent
    has_image = image is not None
    intent = classify_intent(message, has_image)
    print(f"🚦 Routing '{message}' to: {intent}")

    # 3. Execute
    try:
        if intent == "FAST":
            response = FAST_AGENT.run_fast(message, history)
        else:
            # Heavy Agent handles images/tools logic
            # (If you have image processing logic, ensure run_heavy accepts it)
            response = HEAVY_AGENT.run_heavy(message, history)

        # 4. Save & Return
        session_manager.save_session(session_id, response.chat_history)
        
        # Parse JSON if Heavy, or wrap Text if Fast
        raw = response.output
        final_json = {
            "agent_response": raw, 
            "session_id": session_id, 
            "products": []
        }
        
        if intent == "HEAVY":
            # Attempt to parse JSON from heavy agent
            try:
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    final_json.update(parsed)
            except:
                pass # Fallback to raw text

        return final_json

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/history")
async def get_history(token_data: dict = Depends(verify_firebase_token)):
    user_id = token_data.get("uid")
    sessions = session_manager.list_user_sessions(user_id)
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

from pydantic import BaseModel
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
    
    # Simple heuristic title generation
    first_msg = None
    for msg in history:
        if msg.role == "user":
            first_msg = msg.parts[0].text
            break
            
    if not first_msg:
        return {"title": "New Chat"}
        
    words = first_msg.split()[:4]
    title = " ".join(words).title()
    
    session_manager.save_session(req.session_id, history, title=title)
    return {"title": title}

@app.get("/health")
def health_check():
    return {"status": "ContextIQ is Online"}