import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
# Use a separate lightweight client for routing to avoid blocking
router_api_key = os.getenv("GOOGLE_API_KEY")
if router_api_key:
    genai.configure(api_key=router_api_key)

def classify_intent(user_input: str, has_image: bool = False) -> str:
    """
    Returns 'FAST' for chitchat/greetings, 'HEAVY' for shopping/research.
    """
    if has_image:
        return "HEAVY" # Images always need the heavy multimodal agent
    
    # Heuristics for speed (Zero Latency)
    input_lower = user_input.lower().strip()
    fast_triggers = ['hi', 'hello', 'hey', 'good morning', 'thanks', 'cool', 'bye']
    if input_lower in fast_triggers:
        return "FAST"
        
    # If heuristic fails, use a tiny Flash model call
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(
            f"Classify this message as either 'FAST' (greeting, small talk) or 'HEAVY' (shopping request, product search, research).\nMessage: {user_input}\nOutput:",
        )
        return response.text.strip().upper()
    except:
        return "HEAVY" # Default to heavy on error