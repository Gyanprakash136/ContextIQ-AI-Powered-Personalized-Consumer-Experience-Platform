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

        if not os.getenv("GOOGLE_API_KEY"):
            print("WARNING: GOOGLE_API_KEY not set in environment variables")

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
        for attempt in range(retries + 1):
            try:
                return chat.send_message(content)
            except Exception as e:
                err = str(e)
                if ("429" in err or "ResourceExhausted" in err or "Quota" in err) and attempt < retries:
                    wait_time = (attempt + 1) * 5 * backoff_base
                    time.sleep(wait_time)
                    continue
                raise

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
                f"User request: {user_text_query}"
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
            # STATE 2: SEARCH (Tool Execution)
            # ---------------------------------------------------------
            search_results = []
            if not skip_search:
                print("🔄 State: SEARCH")
                search_attempts = 0
                while search_attempts < 2 and not search_results:
                    search_attempts += 1
                    if "search_web" in self.tool_map:
                        try:
                            tool_response = self.tool_map["search_web"](plan_query)
                            if isinstance(tool_response, dict) and tool_response.get("status") == "ok":
                                results = tool_response.get("results", [])
                                if isinstance(results, list):
                                    for item in results:
                                        link = item.get("link")
                                        if link:
                                            self.valid_urls.add(link)
                                    search_results = results
                                    break
                            plan_query = plan_query.replace("site:amazon.in OR site:flipkart.com OR site:myntra.com", "")
                        except Exception:
                            consecutive_failures += 1
                            time.sleep(1.0)
                    else:
                        break

                if not search_results:
                    # If search was attempted but failed, we trigger fallback.
                    # If we skipped search, we just proceed.
                    print("⚠️ Search failed. Triggering Fallback.")
                    return AgentResponse(self._fallback_response(user_text_query), chat.history)

            # ---------------------------------------------------------
            # STATE 3: SCRAPE (Tool Execution)
            # ---------------------------------------------------------
            scraped_products = []
            if not skip_search and search_results:
                print("🔄 State: SCRAPE")
                scrape_candidates = [r.get("link") for r in search_results if r.get("link")]
                scrape_candidates = scrape_candidates[:4] # Limit to 4 scrapes for speed

                for url in scrape_candidates:
                    if url not in self.valid_urls: continue
                    if "scrape_url" not in self.tool_map: continue
                    
                    try:
                        print(f"   Scraping: {url}...")
                        resp = self.tool_map["scrape_url"](url)
                        if isinstance(resp, dict) and resp.get("status") == "ok":
                            prod = resp.get("product")
                            if prod and prod.get("name") and prod.get("price"):
                                scraped_products.append(prod)
                    except Exception:
                        pass
                
                if len(scraped_products) < 1:
                    print("⚠️ Scrape failed (no valid products). Triggering Fallback.")
                    return AgentResponse(self._fallback_response(user_text_query), chat.history)

            # ---------------------------------------------------------
            # STATE 4: EXTRACT & NORMALIZE
            # ---------------------------------------------------------
            normalized = []
            if not skip_search:
                print("🔄 State: EXTRACT")
                for p in scraped_products:
                    try:
                        name = p.get("name")
                        price = p.get("price")
                        image = p.get("image_url") or "https://placehold.co/300x300?text=Product+Image"
                        link = p.get("link") or ""
                        
                        if not name or not price: continue
                        normalized.append({
                            "name": name,
                            "price": price,
                            "link": link,
                            "image_url": image,
                            "reason": p.get("reason", "")
                        })
                    except Exception: continue

            # ---------------------------------------------------------
            # STATE 5: RANK & FILTER
            # ---------------------------------------------------------
            final_list = []
            if not skip_search:
                print("🔄 State: RANK")
                def price_to_number(p_str):
                    try:
                        s = re.sub(r'[^\d.]', '', str(p_str))
                        return float(s) if s else float('inf')
                    except Exception:
                        return float('inf')

                # Sort by price (Low -> High)
                normalized.sort(key=lambda x: price_to_number(x.get("price")))
                
                # Take top 6 verified items
                final_list = normalized[:6]

            # ---------------------------------------------------------
            # STATE 6: SYNTHESIZE (LLM Persona injection)
            # ---------------------------------------------------------
            print("🔄 State: SYNTHESIZE")
            
            synthesis_prompt = (
                "STATE=FORMAT\n"
                f"User Output Logic:\n"
                f"1. IF products are provided: Recommend them as a friendly Shopkeeper.\n"
                f"2. IF products are EMPTY (Chat Mode): Respond to the User's message naturally (e.g. greeting, joke, explanation) without inventing products.\n\n"
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
                print("⚠️ JSON Generation failed. Using fallback formatter.")
                # Fallback to python formatting if LLM JSON fails
                return AgentResponse(self._fallback_response(user_text_query, "JSON Generation Error"), chat.history)

        except Exception as e:
            print(f"🔥 Critical Pipeline Error: {e}")
            fallback = self._fallback_response(user_text_query, error=str(e))
            return AgentResponse(fallback, chat_history)

    def _fallback_response(self, user_input: str, error: Optional[str] = None) -> str:
        """
        Smart Fallback System (3-Tier):
        1. blind_mode: Ask LLM for known products (Best Experience).
        2. hard_backup: If LLM fails, return generic bestsellers (Good Experience).
        3. safety_net: Manual Search Link (Worst Case, but safe).
        """
        # Ensure user_input is a string
        if isinstance(user_input, list): 
             user_input = " ".join([str(p) for p in user_input if isinstance(p, str)])
        
        safe_query = re.sub(r'[^a-zA-Z0-9 ]', '', str(user_input)).replace(" ", "+")
        fallback_link = f"https://www.amazon.in/s?k={safe_query}"

        # Tier 1: Blind Mode (LLM Generation)
        try:
            print(f"⚠️ Triggering Fallback Tier 1 (LLM) for: {user_input}")
            prompt = (
                f"User asked: '{user_input}'\n"
                "External tools (Search) are unavailable.\n"
                "Task: List 3 specific, popular, real-world product models that answer the request.\n"
                "Return JSON ONLY: [{'name': 'Model Name', 'price': 'Approx Price'}, ...]"
            )
            resp = self.model.generate_content(prompt)
            if resp.candidates:
                text = resp.candidates[0].content.parts[0].text
                data = json.loads(extract_json(text))
                
                if isinstance(data, list) and len(data) > 0:
                    products = []
                    for item in data:
                        name = item.get("name", "Generic Product")
                        price = item.get("price", "Check Price")
                        link = f"https://www.amazon.in/s?k={name.replace(' ', '+')}"
                        products.append({
                            "name": name,
                            "price": price,
                            "link": link,
                            "image_url": "https://placehold.co/300x300?text=Product+Image",
                            "reason": "Popular choice (Internal Knowledge)"
                        })
                    
                    payload = {
                        "agent_response": "I couldn't access live search results right now, but here are some popular top-rated options based on my knowledge:",
                        "products": products,
                        "predictive_insight": "You might want to check current availability as these are popular models."
                    }
                    if error: payload["_debug"] = str(error)
                    return json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Fallback Tier 1 Failed: {e}")

        # Tier 2: Hardcoded Backup (If LLM fails)
        # We give at least SOMETHING clickable and relevant-ish
        print("⚠️ Triggering Fallback Tier 2 (Hardcoded)")
        payload = {
            "agent_response": f"I'm having trouble connecting to my tools and my internal database. However, you can check these general categories or use the direct link:",
            "products": [
                {
                    "name": f"Search Results for '{user_input}'",
                    "price": "See Listings",
                    "link": fallback_link,
                    "image_url": "https://placehold.co/300x300?text=Search+Results",
                    "reason": "Direct Search Link"
                },
                {
                    "name": "Bestsellers on Amazon",
                    "price": "Various",
                    "link": "https://www.amazon.in/gp/bestsellers",
                    "image_url": "https://placehold.co/300x300?text=Bestsellers",
                    "reason": "Popular Items"
                }
            ],
            "predictive_insight": "Please try your request again in a moment detailed search."
        }
        if error: payload["_debug"] = str(error)
        return json.dumps(payload, ensure_ascii=False)
