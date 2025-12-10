import os
import pickle
import time
from typing import List, Dict, Any
from datetime import datetime

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

class SessionManager:
    def __init__(self, base_dir=SESSION_DIR):
        self.base_dir = base_dir

    def _get_path(self, session_id: str) -> str:
        return os.path.join(self.base_dir, f"{session_id}.pkl")

    def create_session(self, user_id: str, session_id: str = None) -> str:
        """Creates a new session for the user."""
        if not session_id:
            session_id = f"{user_id}_{int(time.time())}"
        
        data = {
            "session_id": session_id,
            "user_id": user_id,
            "title": "New Chat",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "history": [] 
        }
        self._save(session_id, data)
        return session_id

    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Loads a session's data (history + metadata)."""
        path = self._get_path(session_id)
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def save_session(self, session_id: str, history: List[Any], title: str = None):
        """Updates session history and title."""
        data = self.load_session(session_id)
        # If session doesn't exist (legacy migration), create wrapper
        if not data:
            # Try to see if it was a legacy raw history file
            # But here we assume we are fully switching.
            # If completely new, we might need basic structure.
            data = {
                "session_id": session_id,
                "user_id": "unknown", # Should pass user_id if creating new, but save_session implies existing
                "created_at": datetime.now(),
                "history": []
            }
        
        data["history"] = history
        data["updated_at"] = datetime.now()
        if title:
            data["title"] = title
            
        self._save(session_id, data)

    def _save(self, session_id: str, data: Dict[str, Any]):
        with open(self._get_path(session_id), "wb") as f:
            pickle.dump(data, f)

    def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Lists all sessions for a user, sorted by recency."""
        sessions = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith(".pkl"):
                try:
                    path = os.path.join(self.base_dir, filename)
                    with open(path, "rb") as f:
                        data = pickle.load(f)
                        
                        # Handle legacy raw list files (migration check)
                        if isinstance(data, list):
                            continue # Skip legacy or migrate them
                            
                        if data.get("user_id") == user_id:
                            sessions.append({
                                "id": data["session_id"],
                                "title": data.get("title", "Untitled Chat"),
                                "updated_at": data.get("updated_at"),
                                "preview": str(data["history"][-1].parts[0].text)[:50] if data["history"] else "Empty"
                            })
                except Exception:
                    continue
        
        # Sort by updated_at desc
        return sorted(sessions, key=lambda x: x.get("updated_at", datetime.min), reverse=True)

# Singleton instance
session_manager = SessionManager()