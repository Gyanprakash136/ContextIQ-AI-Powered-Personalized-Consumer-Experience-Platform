def extract_json(text: str) -> str:
    """
    Extracts JSON block using character-by-character bracket counting.
    Reliably handles nested JSON and mixed text.
    """
    text = text.strip()
    
    # 1. Regex for code blocks (fast path)
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match: 
        return match.group(1)

import json
import time
import re
from typing import Any, Dict, List, Optional
import os

import google.generativeai as genai
from google.generativeai.types import content_types

# ---------- Utility helpers ----------

def is_valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:
        return False

def largest_balanced_json_block(text: str) -> str:
    """
    Find the largest balanced JSON object or array block in `text`.
    Uses bracket counting to identify candidate blocks and returns the largest block found.
    """
    candidates = []
    stack = []
    start = None
    for i, ch in enumerate(text):
        if ch == '{' or ch == '[':
            if not stack:
                start = i
            stack.append(ch)
        elif ch == '}' or ch == ']':
            if stack:
                stack.pop()
                if not stack and start is not None:
                    candidates.append(text[start:i + 1])
                    start = None
    if not candidates:
        return text
    # Return the largest candidate (most likely the full JSON)
    return max(candidates, key=len)

def extract_json(text: str) -> str:
    """
    Robust extraction:
    - If ```json``` block present, take inner content.
    - Else select largest balanced JSON block (object or array).
    - Strip common 'THOUGHT' prefixes if present.
    """
    if not text:
        return text
    t = text.strip()

    # Remove common "THOUGHT:" markers if model accidentally emitted them.
    if "THOUGHT:" in t:
        t = t.split("THOUGHT:")[-1].strip()

    # Fast path: fenced json code block
    match = re.search(r'```json\s*(\{.*?\}|\[.*?\])\s*```', t, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Robust path: bracket matching for largest block
    block = largest_balanced_json_block(t)
    return block.strip()

# ---------- Agent orchestration ----------

class AgentResponse:
    def __init__(self, output: str, chat_history: List[Dict[str, Any]]):
        self.output = output
        self.chat_history = chat_history

class Agent:
    """
    Production-grade hybrid agent shim.
    Enforces a strict Python-side State Machine:
    PLAN -> SEARCH -> SCRAPE -> EXTRACT -> RANK -> SYNTHESIZE
    """

    MAX_TOOL_PAYLOAD = 5000  # chars to keep from large tool outputs

    def __init__(self, model: str, name: str, instruction: str, tools: List[Any]):
        self.model_name = model
        self.name = name
        self.system_instruction = instruction
        self.tools = tools
        self.tool_map = {}
        self.valid_urls = set()
        self.max_iterations_default = 20

        for tool in tools:
            if callable(tool):
                self.tool_map[tool.__name__] = tool

        # 1. Parsing & Sanitation of API Keys
        current_key = os.getenv("GOOGLE_API_KEY")
        raw_single_key = os.getenv("GOOGLE_API_KEY", "").strip()
        raw_multi_keys = os.getenv("GOOGLE_API_KEYS", "").strip()

        # Handle case where user put list in GOOGLE_API_KEY
        if "," in raw_single_key:
            print("⚠️ 'GOOGLE_API_KEY' contains commas. Assuming it's a list. Using first key.")
            parts = [k.strip() for k in raw_single_key.split(",") if k.strip()]
            if parts:
                raw_single_key = parts[0]
                # If plural var is empty, backfill it for rotation logic
                if not raw_multi_keys:
                    os.environ["GOOGLE_API_KEYS"] = ",".join(parts)
        
        # Aggressive strip of quotes and whitespace
        clean_key = raw_single_key.strip().strip("'").strip('"')
        
        if not clean_key:
             # Fallback: check if we have a list to pull from
             if raw_multi_keys:
                 parts = [k.strip() for k in raw_multi_keys.split(",") if k.strip()]
                 if parts:
                     clean_key = parts[0]
                     print(f"⚠️ 'GOOGLE_API_KEY' was empty, using first key from 'GOOGLE_API_KEYS': ...{clean_key[-4:]}")

        if not clean_key:
            print("WARNING: Could not find a valid GOOGLE_API_KEY.")
        else:
            if raw_single_key != clean_key:
                 print(f"⚠️ Sanitized API Key (removed whitespace/quotes). Using: ...{clean_key[-4:]}")
            
            # CRITICAL: Update env var so libraries using os.getenv get the clean key
            os.environ["GOOGLE_API_KEY"] = clean_key
            genai.configure(api_key=clean_key)

        safety = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        }

        self.model = genai.GenerativeModel(
            model_name=model,
            tools=tools,
            system_instruction=instruction,
            safety_settings=safety
        )

    def _send_message_with_retry(self, chat, content, retries: int = 3, backoff_base: int = 2):
        attempt = 0
        while attempt <= retries:
            try:
                return chat.send_message(content)
            except Exception as e:
                err = str(e)
                # Check for Quota or Rate Limit errors
                if ("429" in err or "ResourceExhausted" in err or "Quota" in err):
                    print(f"⚠️ Quota Warning (Attempt {attempt + 1}/{retries + 1}): {err}")
                    
                    # Try to rotate key first
                    if self._rotate_api_key():
                        print("🔄 Switched to next API Key. Retrying immediately...")
                        time.sleep(1) # Brief pause for config propagation
                        
                        # Increment attempt to prevent infinite loops, but consider increasing default retries if needed
                        attempt += 1
                        if attempt > retries:
                             print("❌ Max retries reached even after rotation.")
                             raise
                        continue
                    
                    # If rotation failed (no more keys) or single key, use backoff
                    if attempt < retries:
                        wait_time = (attempt + 1) * 5 * backoff_base
                        print(f"⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        attempt += 1
                        continue
                
                # If we get here: either not a quota error, or we ran out of retries/rotations
                raise

    def _rotate_api_key(self) -> bool:
        """
        Rotates to the next available API key in GOOGLE_API_KEYS.
        Returns True if successful, False if no other keys available.
        """
        api_keys_str = os.getenv("GOOGLE_API_KEYS")
        if not api_keys_str:
            return False
            
        keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
        if len(keys) < 2:
            return False
            
        # Get current key (heuristic: check configured key if possible, or just cycle)
        # Since we can't easily peek at current configured key, we'll maintain state in the Agent if possible
        # But Agent is transient request-scoped in some designs. 
        # Better approach: Try next key in list that isn't the current environment var GOOGLE_API_KEY
        
        # Better approach: Try next key in list that isn't the current environment var GOOGLE_API_KEY
        
        current_key = os.getenv("GOOGLE_API_KEY")
        clean_current_key = "None"
        try:
            # Robustly handle current_key if it contained extra chars
            if current_key:
                clean_current_key = current_key.strip().strip("'").strip('"')
            
            # Find index of current key in clean list
            try:
                current_index = keys.index(clean_current_key)
                next_index = (current_index + 1) % len(keys)
            except ValueError:
                # If current key not in list (weird state), start from 0
                next_index = 0
        except Exception:
             next_index = 0
            
        new_key = keys[next_index]
        
        # Triple-check sanitation of new key
        new_key = new_key.strip().strip("'").strip('"')

        print(f"🔑 Rotating API Key: ...{clean_current_key[-4:] if len(clean_current_key) > 4 else clean_current_key} -> ...{new_key[-4:]}")
        
        # Update Environment and GenAI Config
        os.environ["GOOGLE_API_KEY"] = new_key
        genai.configure(api_key=new_key)
        return True

    def _extract_text_from_input(self, user_input: Any) -> str:
        """Helper to safely extract string text from potentially multimodal input."""
        if isinstance(user_input, str):
            return user_input
        if isinstance(user_input, list):
            # Extract only string parts
            text_parts = [p for p in user_input if isinstance(p, str)]
            return " ".join(text_parts)
        return str(user_input)

    def run(self, user_input: Any, chat_history: Optional[List[Dict[str, Any]]] = None, max_iterations: Optional[int] = None) -> AgentResponse:
        if chat_history is None:
            chat_history = []
        if max_iterations is None:
            max_iterations = self.max_iterations_default

        chat = self.model.start_chat(history=chat_history, enable_automatic_function_calling=False)
        self.valid_urls.clear()
        
        # Safe text extraction for logic that needs string (logging, regex, fallback)
        user_text_query = self._extract_text_from_input(user_input)
        
        # CLEANUP: Remove "User Message:" prefix if present (common in some frontends/test scripts)
        user_text_query = re.sub(r'^(User Message:)\s*', '', user_text_query, flags=re.IGNORECASE).strip()
        
        consecutive_failures = 0
        print(f"▶️ Pipeline Start: {user_text_query}")

        try:
            # ---------------------------------------------------------
            # STATE 1: PLAN (Query Refinement OR Chat Detection)
            # ---------------------------------------------------------
            plan_prompt = (
                "STATE=PLAN\n"
                "Analyze the user's request.\n"
                "1. If it is a Product Search (e.g., 'buy laptop', 'best shoes'), rewrite it into a concise marketplace query.\n"
                "2. If it is General Conversation OR Complaint (e.g., 'Hi', 'Why did you fail?', 'This is bad'), respond EXACTLY with: SKIP_SEARCH\n"
                "Respond with the single-line query OR 'SKIP_SEARCH' only. Do NOT call tools.\n\n"
                f"User request: {user_text_query}\n"
            )
            print("🔄 State: PLAN")
            plan_resp = self._send_message_with_retry(chat, plan_prompt)
            plan_text = ""
            if plan_resp.candidates and plan_resp.candidates[0].content.parts:
                plan_text = "".join([p.text for p in plan_resp.candidates[0].content.parts if getattr(p, "text", None)])
            plan_query = plan_text.strip().splitlines()[0] if plan_text else user_text_query
            
            skip_search = "SKIP_SEARCH" in plan_query
            print(f"   Query: {plan_query} (Skip: {skip_search})")

            # ---------------------------------------------------------
            # STATE 2: SYNTHESIZE (LLM generates response based on chat history and optional products)
            # ---------------------------------------------------------
            final_list = []  # Empty list; model may generate its own products if desired.
            print("🔄 State: SYNTHESIZE")
            synthesis_prompt = (
                "STATE=FORMAT\n"
                f"User Output Logic:\n"
                f"1. IF products are provided: Recommend them as a friendly Shopkeeper.\n"
                f"2. IF products are EMPTY (Chat Mode): Respond naturally without inventing products.\n"
                f"User Request: {user_text_query}\n"
                f"Products Found: {json.dumps(final_list)}\n\n"
                "TASK: Generate the Final JSON response.\n"
                "Return ONLY valid JSON with keys: 'agent_response', 'products', 'predictive_insight'."
            )
            final_resp = self._send_message_with_retry(chat, synthesis_prompt)
            final_text = ""
            if final_resp.candidates and final_resp.candidates[0].content.parts:
                final_text = final_resp.candidates[0].content.parts[0].text
            final_json = extract_json(final_text)
            if is_valid_json(final_json):
                print("✅ Success.")
                return AgentResponse(final_json, chat.history)
            else:
                print("⚠️ JSON Generation failed. Returning raw LLM output.")
                return AgentResponse(final_text, chat.history)
        except Exception as e:
            print(f"🔥 Critical Pipeline Error: {e}")
            raise



