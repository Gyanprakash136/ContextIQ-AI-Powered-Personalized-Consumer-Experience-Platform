from core.shim import Agent
from core.prompts import AGENT_INSTRUCTION
# Deployment Fix: Forced Cache Bust [Timestamp Verified]

def get_tool_list():
    return []

def build_contextiq_agent():
    print(" Building ContextIQ Agent...")
    
    tools = get_tool_list()
    print(f" Loaded Tools: {[t.__name__ for t in tools]}")
    # Initialize Agent
    agent = Agent(
        model="gemini-1.5-pro",
        name="ContextIQ_Assistant",
        instruction=AGENT_INSTRUCTION,
        tools=tools
    )
    
    return agent