
import google.generativeai as genai
from google.generativeai.types import content_types
from collections.abc import Iterable
import os

class Agent:
    def __init__(self, model: str, name: str, instruction: str, tools: list):
        self.model_name = model
        self.name = name
        self.system_instruction = instruction
        self.tools = tools
        
        # Configure GenAI (assumes configure was called globally or we do it here)
        if not os.getenv("GOOGLE_API_KEY"):
            print("WARNING: GOOGLE_API_KEY not set in environment")
            
        self.model = genai.GenerativeModel(
            model_name=model,
            tools=tools,
            system_instruction=instruction
        )

    def run(self, input, chat_history: list = None):
        """
        Runs the agent with the given input and history.
        input: str or list of [str, PIL.Image, etc.]
        """
        if chat_history is None:
            chat_history = []

        # Convert simple internal history format to Gemini format if needed
        # Assuming chat_history is list of dicts: {"role": "user"/"model", "parts": ["..."]}
        # or list of Content objects.
        
        # Start a chat session
        chat = self.model.start_chat(
            history=chat_history,
            enable_automatic_function_calling=True
        )
        
        try:
            response = chat.send_message(input)
            
            # Return a simple object that mimics the expected structure from original code
            return AgentResponse(
                output=response.text,
                chat_history=chat.history
            )
        except Exception as e:
            print(f"Agent Error: {e}")
            return AgentResponse(
                output=f"I encountered an error: {str(e)}",
                chat_history=chat_history
            )

class AgentResponse:
    def __init__(self, output, chat_history):
        self.output = output
        self.chat_history = chat_history
