
import os
from core.shim import Agent
from tools.vector_db import search_internal_catalog
from tools.predictor import generate_future_insight
from tools.scraper import scrape_url
from core.prompts import AGENT_INSTRUCTION

def get_tool_list():
    """
    Returns the list of tools. 
    """
    # Simply return the functions. Standard genai.GenerativeModel accepts a list of functions.
    return [scrape_url, search_internal_catalog, generate_future_insight]

def build_contextiq_agent():
    print("🚀 Building ContextIQ Agent...")
    
    # Initialize Agent
    agent = Agent(
        model="gemini-2.5-pro",
        name="ContextIQ_Assistant",
        instruction=AGENT_INSTRUCTION,
        tools=get_tool_list() 
    )
    
    return agent