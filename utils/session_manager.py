from google.adk.memory import InMemoryChatMessageHistory

# Global storage for active sessions
# In a real production app, you would use Redis or a Database
session_store = {}

def get_session_history(session_id: str):
    """
    Retrieves or creates a chat history for a specific user session.
    """
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    
    return session_store[session_id]

def clear_session(session_id: str):
    """
    Resets the chat history for a user (useful for 'New Chat' button).
    """
    if session_id in session_store:
        del session_store[session_id]
        return True
    return False