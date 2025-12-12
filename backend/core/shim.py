import os
import json
import re
import time
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from tools.search_tool import search_web
from tools.scraper import scrape_url

class AgentResponse:
    def __init__(self, output: str, chat_history: List[Dict[str, Any]]):
        self.output = output
        self.chat_history = chat_history

class Agent:
    def __init__(self, model: str, name: str, instruction: str):
        self.model_name = model
        self.instruction = instruction
        
        # Configure API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: print("❌ Error: GOOGLE_API_KEY not found")
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=instruction
        )

    def run_fast(self, user_input: str, chat_history: list) -> AgentResponse:
        """Direct Chat for 'Hey', 'Hello' - No Tools, No Delays"""
        chat = self.model.start_chat(history=chat_history)
        response = chat.send_message(user_input)
        return AgentResponse(response.text, chat.history)

    def run_heavy(self, user_input: Any, chat_history: list) -> AgentResponse:
        """
        Agentic Workflow: Plan -> Search -> Scrape -> Answer
        """
        chat = self.model.start_chat(history=chat_history)
        
        # --- STEP 1: PLAN ---
        print(f"🤖 [Agent] Planning for: {user_input}")
        plan_prompt = (
            f"User Request: {user_input}\n"
            "Do I need external information to answer this? "
            "If yes, output: 'SEARCH: <search_query>'\n"
            "If no, output: 'ANSWER'\n"
        )
        plan_resp = chat.send_message(plan_prompt)
        decision = plan_resp.text.strip()
        
        context_data = ""
        
        # --- STEP 2: TOOL EXECUTION ---
        if "SEARCH:" in decision:
            query = decision.replace("SEARCH:", "").strip()
            print(f"🔎 [Agent] Searching: {query}")
            
            # 1. Search Web
            search_results = search_web(query)
            context_data += f"\n--- SEARCH RESULTS ---\n{search_results}\n"
            
            # 2. Extract first valid link to scrape (Autonomously)
            # Simple heuristic: find first http link in search results
            match = re.search(r'(https?://[^\s]+)', search_results)
            if match:
                url = match.group(1)
                print(f"🕷️ [Agent] Scraping: {url}")
                scraped_text = scrape_url(url)
                context_data += f"\n--- CONTENT FROM {url} ---\n{scraped_text[:10000]}\n"

        # --- STEP 3: SYNTHESIZE ---
        print("🧠 [Agent] Synthesizing Final Answer")
        final_prompt = (
            f"Original Request: {user_input}\n"
            f"Gathered Context: {context_data}\n"
            "Task: Provide the final helpful response. "
            "If you found products, output them in the required JSON format."
        )
        
        final_resp = chat.send_message(final_prompt)
        return AgentResponse(final_resp.text, chat.history)