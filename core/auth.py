
import firebase_admin
from firebase_admin import auth, credentials
import os
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

# Define the security scheme
security = HTTPBearer()

# Initialize Firebase on module load (or lazily)
def initialize_firebase():
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Not initialized, try to load credentials
        cred_path = os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print(f"🔥 Firebase Admin initialized with {cred_path}")
        else:
            print(f"⚠️ Warning: Firebase Credentials not found at {cred_path}. Auth verification will fail.")
            # For hackathons, sometimes people want to bypass locally, but let's be strict by default.
            # If you want to mock it, we can add a MOCK_AUTH env var.

# Initialize immediately
initialize_firebase()

async def verify_firebase_token(res: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifies the Firebase ID Token passed in the Authorization header.
    Returns the decoded token (dict) which includes the 'uid'.
    """
    token = res.credentials
    
    # Check for Mock Mode (Useful for testing without keys)
    # ALSO allow explicit "mock_token" for dev testing
    if os.getenv("MOCK_AUTH") == "true" or token == "mock_token":
        return {"uid": "mock_user_123", "email": "mock@example.com"}

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Authentication Token: {str(e)}"
        )

def get_current_user_id(token_data: dict) -> str:
    """Helper to extract UID from verified token"""
    return token_data.get("uid")
