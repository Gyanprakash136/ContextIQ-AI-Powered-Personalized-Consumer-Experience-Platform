from core.shim import Agent
from core.prompts import AGENT_INSTRUCTION

def build_fast_agent():
    return Agent(
        model="gemini-1.5-flash-001",
        name="ContextIQ_Speed",
        instruction="You are a helpful assistant. Keep responses short, friendly, and natural. Do not generate JSON."
    )

def build_heavy_agent():
    return Agent(
        model="gemini-1.5-pro-001", # Use Pro for reasoning
        name="ContextIQ_Brain",
        instruction=AGENT_INSTRUCTION
    )