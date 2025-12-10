from core.shim import Agent
from tools.predictor import generate_future_insight
from tools.scraper import scrape_url
from core.prompts import AGENT_INSTRUCTION
from tools.deprecated_tool import search_internal_catalog

from tools.search_tool import search_web

def get_tool_list():
    """
    Returns the list of tools. 
    """
    # Simply return the functions. Standard genai.GenerativeModel accepts a list of functions.
    return [scrape_url, generate_future_insight, search_web, search_internal_catalog]

def build_contextiq_agent():
    print("🚀 Building ContextIQ Agent...")
    
    tools = get_tool_list()
    print(f"🔧 Loaded Tools: {[t.__name__ for t in tools]}")
    # Initialize Agent
    agent = Agent(
        model="gemini-2.5-flash",
        name="ContextIQ_Assistant",
        instruction=AGENT_INSTRUCTION,
        tools=get_tool_list() 
    )
    
    return agent