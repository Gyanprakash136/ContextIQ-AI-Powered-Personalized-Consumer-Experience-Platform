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

        # Store config for fallback re-initialization
        self.model_name = model
        self.tools = tools
        self.instruction = instruction
        self.safety = safety
        
        # Fallback Hierarchy: Requested -> Flash (Speed/Cost) -> Pro (Quality/Stability)
        self.fallback_chain = []
        if model not in ["gemini-1.5-flash", "gemini-1.5-pro"]:
             self.fallback_chain.append(model)
        # Use specific versions to avoid alias 404s
        self.fallback_chain.extend(["gemini-1.5-flash", "gemini-1.5-pro-001", "gemini-1.0-pro"])
        
        self.current_model_index = 0
        self._init_model(self.fallback_chain[0])

    def _init_model(self, model_name):
        print(f"🤖 Initializing Agent with Model: {model_name}")
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=self.tools,
            system_instruction=self.instruction,
            safety_settings=self.safety
        )

    def _send_message_with_retry(self, chat, content, retries: int = 10, backoff_base: int = 2):
        attempt = 0
        while attempt <= retries:
            try:
                return chat.send_message(content)
            except Exception as e:
                err = str(e)
                # Check for Quota or Rate Limit errors
                if ("429" in err or "ResourceExhausted" in err or "Quota" in err):
                    print(f"⚠️ Quota Warning (Attempt {attempt + 1}/{retries + 1}): {err[:100]}...")

                    # Intelligent Backoff
                    wait_match = re.search(r'retry in (\d+(\.\d+)?)s', err)
                    if wait_match:
                        forced_wait = float(wait_match.group(1))
                        if forced_wait < 120:
                             print(f"🛑 Upstream requested wait: {forced_wait}s. Sleeping...")
                             time.sleep(forced_wait + 1) 
                             attempt += 1
                             continue
                    
                    # Try to rotate key first
                    if self._rotate_api_key():
                        print("🔄 Switched to next API Key. Retrying immediately...")
                        time.sleep(2)
                        attempt += 1
                        if attempt > retries:
                             raise
                        continue
                    
                    # Backoff
                    if attempt < retries:
                        wait_time = (attempt + 1) * 3 * backoff_base 
                        print(f"⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        attempt += 1
                        continue
                
                print(f"❌ Unrecoverable Error or Retries Exhausted: {err}")
                raise

        raise Exception(f"Max retries ({retries}) exceeded without success.")

    def _switch_model(self) -> bool:
        """Switches to the next model in the fallback chain."""
        next_idx = self.current_model_index + 1
        if next_idx < len(self.fallback_chain):
            self.current_model_index = next_idx
            new_model = self.fallback_chain[next_idx]
            print(f"⚠️ Primary model failed. Falling back to: {new_model}")
            self._init_model(new_model)
            return True
        return False

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
            
        current_key = os.getenv("GOOGLE_API_KEY")
        clean_current_key = "None"
        try:
            if current_key:
                clean_current_key = current_key.strip().strip("'").strip('"')
            try:
                current_index = keys.index(clean_current_key)
                next_index = (current_index + 1) % len(keys)
            except ValueError:
                next_index = 0
        except Exception:
             next_index = 0
            
        new_key = keys[next_index]
        new_key = new_key.strip().strip("'").strip('"')

        print(f"🔑 Rotating API Key: ...{clean_current_key[-4:] if len(clean_current_key) > 4 else clean_current_key} -> ...{new_key[-4:]}")
        
        os.environ["GOOGLE_API_KEY"] = new_key
        genai.configure(api_key=new_key)
        return True

    def _extract_text_from_input(self, user_input: Any) -> str:
        """Helper to safely extract string text from potentially multimodal input."""
        if isinstance(user_input, str):
            return user_input
        if isinstance(user_input, list):
            text_parts = [p for p in user_input if isinstance(p, str)]
            return " ".join(text_parts)
        return str(user_input)

    def run(self, user_input: Any, chat_history: Optional[List[Dict[str, Any]]] = None, max_iterations: Optional[int] = None) -> AgentResponse:
        """
        Main entry point for "Pure Conversation" mode.
        Incorporates Model Fallback Strategy.
        """
        if chat_history is None:
            chat_history = []
        
        # 1. Start Chat Session (handling model fallback loop)
        while True:
            try:
                # Need to use self.model which is current model (initially requested or fallback)
                chat = self.model.start_chat(history=chat_history)
                
                # 2. PLAN Step
                plan_prompt = (
                    f"User Input: {user_input}\n"
                    "State: PLAN\n"
                    "Decide if external info is needed (SEARCH) or if you can answer directly (SKIP_SEARCH).\n"
                    "Respond with JUST the query strings or 'SKIP_SEARCH'."
                )
                print("🔄 State: PLAN")
                plan_resp = self._send_message_with_retry(chat, plan_prompt)
                
                if plan_resp.candidates and plan_resp.candidates[0].content.parts:
                    raw_plan = plan_resp.text.strip()
                else:
                    raw_plan = "SKIP_SEARCH" 
                    
                print(f"   Query: {raw_plan}")
                
                # 3. SYNTHESIZE Step
                synth_prompt = (
                    f"Original User Input: {user_input}\n"
                    f"Plan/Search Results: {raw_plan}\n" 
                    "State: SYNTHESIZE\n"
                    "Generate the final JSON response."
                )
                print("🔄 State: SYNTHESIZE")
                final_resp = self._send_message_with_retry(chat, synth_prompt)
                
                json_text = extract_json(final_resp.text)
                print("✅ Success.")
                return AgentResponse(output=json_text)
                
            except Exception as e:
                print(f"❌ Error in run loop: {e}")
                # Try to switch models if we failed (likely due to persistent Quota issues)
                if self._switch_model():
                    print("🔁 Retrying entire run with new model...")
                    time.sleep(1)
                    continue
                else:
                     # No more models, re-raise
                     raise e
                     # No more models, re-raise
                     raise e
