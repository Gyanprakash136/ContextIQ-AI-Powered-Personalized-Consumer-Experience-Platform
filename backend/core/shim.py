import google.generativeai as genai
from google.generativeai.types import content_types
from collections.abc import Iterable
import os
import time

class Agent:
    def __init__(self, model: str, name: str, instruction: str, tools: list):
        self.model_name = model
        self.name = name
        self.system_instruction = instruction
        self.tools = tools
        self.tool_map = {}  # Map function names to actual functions
        
        # Build tool map from tools list
        for tool in tools:
            if callable(tool):
                self.tool_map[tool.__name__] = tool
        
        if not os.getenv("GOOGLE_API_KEY"):
            print("WARNING: GOOGLE_API_KEY not set in environment")
            
        # Configure GenAI with safety settings
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

    def run(self, input, chat_history: list = None, max_iterations: int = 25):
        """
        Manual tool orchestration loop.
        Disables automatic function calling and manages tool execution manually.
        Max 25 iterations to allow for deep scraping (3-10 products) + analysis.
        """
        if chat_history is None:
            chat_history = []

        # Start chat WITHOUT automatic function calling
        chat = self.model.start_chat(
            history=chat_history,
            enable_automatic_function_calling=False  # MANUAL CONTROL
        )
        
        iteration = 0
        
        try:
            # Initial message
            response = chat.send_message(input)
            
            # Orchestration loop
            while iteration < max_iterations:
                iteration += 1
                print(f"\n🔄 Iteration {iteration}/{max_iterations}")
                
                # RETRY LOGIC FOR GOOGLE API QUOTA
                retry_count = 0
                max_retries = 3
                current_response = None
                
                while retry_count <= max_retries:
                    try:
                        if start_new_turn:
                             # This is the first call of the loop or a new turn after tool output
                             if function_responses:
                                  current_response = chat.send_message(function_responses)
                                  function_responses = None # Clear after sending
                             else:
                                  # Should typically not happen here unless logic flow changes, 
                                  # but provided for safety if moved
                                  pass 
                        else:
                             # Should have been handled before loop or previous iteration
                             pass
                        break # Success
                    except Exception as e:
                        if "429" in str(e) or "ResourceExhausted" in str(e) or "Quota exceeded" in str(e):
                            retry_count += 1
                # Check if we have a text response
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    
                    print(f"   Finish Reason: {candidate.finish_reason}")
                    
                    # Check for function calls
                    function_calls = []
                    text_parts = []
                    
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            function_calls.append(part.function_call)
                        elif hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    
                    # If we have text and no pending function calls, we're done
                    if text_parts and not function_calls:
                        text_output = "".join(text_parts)
                        print(f"✅ Final response: {len(text_output)} characters")
                        return AgentResponse(
                            output=text_output,
                            chat_history=chat.history
                        )
                    
                    # If we have function calls, execute them
                    if function_calls:
                        print(f"   📞 Function calls requested: {len(function_calls)}")
                        
                        # Execute each function call
                        function_responses = []
                        for fc in function_calls:
                            func_name = fc.name
                            func_args = dict(fc.args)
                            
                            print(f"      Calling: {func_name}")
                            
                            if func_name in self.tool_map:
                                try:
                                    result = self.tool_map[func_name](**func_args)
                                    result_str = str(result)
                                    print(f"      ✅ Result: {len(result_str)} chars")
                                    
                                    # Create function response
                                    function_responses.append(
                                        genai.protos.Part(
                                            function_response=genai.protos.FunctionResponse(
                                                name=func_name,
                                                response={"result": result_str}
                                            )
                                        )
                                    )
                                except Exception as e:
                                    print(f"      ❌ Error in tool {func_name}: {e}")
                                    function_responses.append(
                                        genai.protos.Part(
                                            function_response=genai.protos.FunctionResponse(
                                                name=func_name,
                                                response={"error": str(e)}
                                            )
                                        )
                                    )
                            else:
                                print(f"      ⚠️  Unknown function: {func_name}")
                                function_responses.append(
                                    genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name=func_name,
                                            response={"error": f"Function {func_name} not found"}
                                        )
                                    )
                                )
                        
                        # Send function responses back to model
                        response = self._send_message_with_retry(chat, function_responses)
                        continue  # Loop again
                    
                    
                    # No text and no function calls - check finish reason
                    if candidate.finish_reason in [1, 2, 3, 4, 5]:  # STOP, MAX_TOKENS, SAFETY, RECITATION, OTHER
                        print(f"⚠️  Model stopped with finish_reason: {candidate.finish_reason}")
                        
                        # Try to extract any accumulated text from history
                        accumulated_text = []
                        # Look explicitly at the last message from model
                        if chat.history and chat.history[-1].role == 'model':
                            last_msg = chat.history[-1]
                            for part in last_msg.parts:
                                if hasattr(part, 'text') and part.text:
                                    accumulated_text.append(part.text)
                        
                        if accumulated_text:
                            return AgentResponse(
                                output="".join(accumulated_text),
                                chat_history=chat.history
                            )
                        else:
                             # Fallback if no text found
                            return AgentResponse(
                                output="I apologize, but I couldn't generate a complete response. Please try again.",
                                chat_history=chat.history
                            )

                    print("⚠️  No text or function calls in response")
                    break
                else:
                    print("⚠️  No candidates in response")
                    break
            
            # If we exit the loop without returning, we hit max iterations
            print(f"⚠️  Max iterations ({max_iterations}) reached")
            
            return AgentResponse(
                output="I apologize, but I couldn't complete the request within the allowed steps.",
                chat_history=chat.history
            )
            
        except Exception as e:
            print(f"❌ Agent Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return AgentResponse(
                output=f"I encountered an error: {str(e)}",
                chat_history=chat_history
            )

class AgentResponse:
    def __init__(self, output, chat_history):
        self.output = output
        self.chat_history = chat_history
