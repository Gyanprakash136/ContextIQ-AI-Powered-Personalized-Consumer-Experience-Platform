
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load ENV from backend/.env if running from root
load_dotenv("backend/.env")

# Shim logic reproduction
def debug_tier1_fallback(user_input):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ SKIPPING: No GOOGLE_API_KEY")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash") # Use flash for speed/testing

    print(f"Testing Fallback Tier 1 for: '{user_input}'")
    
    prompt = (
        f"User asked: '{user_input}'\n"
        "External tools unavailable.\n"
        "Task: List 3 real, popular product models relevant to this request.\n"
        "Format: JSON Array ONLY. Example: [{'name': 'MacBook Air M2', 'price': '₹99,000'}, {'name': 'Dell XPS 13', 'price': '₹1,20,000'}]\n"
        "Do NOT include markdown backticks."
    )

    try:
        resp = model.generate_content(prompt)
        text = resp.text
        print(f"\n--- RAW LLM OUTPUT ---\n{text}\n----------------------")
        
        # Exact cleanup logic from shim.py
        clean_text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        print("\n✅ JSON PARSE SUCCESS:")
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"\n❌ JSON PARSE FAILED: {e}")

if __name__ == "__main__":
    debug_tier1_fallback("suggest me a laptop")
    debug_tier1_fallback("buy nike shoes")
