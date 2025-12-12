import re

# Helper for robust JSON extraction
def extract_json(text: str) -> str:
    """Extracts JSON block from mixed text using regex and bracket counting."""
    # 1. Try regex for code blocks first
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match: return match.group(1)
    
    # 2. Try finding the outermost braces
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match: return match.group(0)

    # 3. Fallback: Return original (validation will fail if it's not JSON)
    return text

class Agent:
    def __init__(self, model: str, name: str, instruction: str, tools: list):
        self.model_name = model
        self.name = name
        self.system_instruction = instruction
        self.tools = tools
        self.tool_map = {}

        # Build map of tool name -> function
        for tool in tools:
            if callable(tool):
                self.tool_map[tool.__name__] = tool

        if not os.getenv("GOOGLE_API_KEY"):
            print("WARNING: GOOGLE_API_KEY not set in environment variables")

        safety = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
        }

        self.model = genai.GenerativeModel(
            model_name=model,
            tools=tools,
            system_instruction=instruction,
            safety_settings=safety
        )


    def _send_message_with_retry(self, chat, content, retries=3):
        """Send a message with exponential backoff retries."""
        for attempt in range(retries + 1):
            try:
                return chat.send_message(content)
            except Exception as e:
                err = str(e)
                if ("429" in err or "ResourceExhausted" in err or "Quota" in err) and attempt < retries:
                    wait_time = (attempt + 1) * 20
                    print(f"Rate limit. Waiting {wait_time}s (attempt {attempt+1}/{retries})")
                    time.sleep(wait_time)
                else:
                    raise


    def run(self, user_input, chat_history=None, max_iterations=12):
        """
        Hybrid Thought-Action Loop.
        Enforces 7-step workflow, correct JSON, and robust error handling.
        """
        if chat_history is None:
            chat_history = []

        chat = self.model.start_chat(
            history=chat_history,
            enable_automatic_function_calling=False
        )

        # Tool Guardrails
        tool_usage_count = {} 
        consecutive_failures = 0
        
        try:
            # Initial Prompt
            print(f"▶️ User Input: {user_input}")
            response = self._send_message_with_retry(chat, user_input)

            iteration = 0
            while iteration < max_iterations:
                iteration += 1
                print(f"\n🔄 Step {iteration} (Failures: {consecutive_failures})")

                if not response.candidates:
                    print("❌ No candidates received.")
                    break

                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason
                
                # Parse Output
                function_calls = []
                text_parts = []
                for part in candidate.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        function_calls.append(part.function_call)
                    elif hasattr(part, "text") and part.text:
                        text_parts.append(part.text)

                combined_text = "".join(text_parts).strip()
                
                # [1] THOUGHT LOGGING & SAFETY
                if "THOUGHT:" in combined_text:
                    thought_part = combined_text.split("THOUGHT:", 1)[1]
                    # Log it but DON'T let it leak into JSON processing if possible
                    # We will strip it out later during JSON extraction
                    thought_preview = thought_part.split("\n", 1)[0].strip()
                    print(f"🧠 THOUGHT: {thought_preview}")

                # [2] HANDLE TOOL CALLS
                if function_calls:
                    print(f"🛠  Tools requested: {len(function_calls)}")
                    tool_responses = []
                    
                    for fc in function_calls:
                        func_name = fc.name
                        func_args = dict(fc.args)

                        # Guardrail: Prevent >2 identical calls
                        call_sig = f"{func_name}:{json.dumps(func_args, sort_keys=True)}"
                        tool_usage_count[call_sig] = tool_usage_count.get(call_sig, 0) + 1
                        
                        if tool_usage_count[call_sig] > 2:
                            print(f"🛑 Blocking duplicate tool call: {func_name}")
                            tool_responses.append(
                                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                                    name=func_name, response={"error": "STOP. You are repeating yourself. Move to next step."}
                                ))
                            )
                            continue

                        # Execute Tool
                        if func_name in self.tool_map:
                            try:
                                print(f"   👉 Executing {func_name}...")
                                result = self.tool_map[func_name](**func_args)
                                
                                # Safety: Normalize output to JSON string and truncate if huge
                                result_str = json.dumps(result)
                                if len(result_str) > 5000:
                                    result_str = result_str[:5000] + "... [TRUNCATED]"
                                
                                tool_responses.append(
                                    genai.protos.Part(function_response=genai.protos.FunctionResponse(
                                        name=func_name, response={"result": result_str}
                                    ))
                                )
                                consecutive_failures = 0 # Reset on success
                            except Exception as e:
                                print(f"   ❌ Tool Error: {e}")
                                tool_responses.append(
                                    genai.protos.Part(function_response=genai.protos.FunctionResponse(
                                        name=func_name, response={"error": str(e)}
                                    ))
                                )
                                consecutive_failures += 1
                        else:
                            tool_responses.append(
                                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                                    name=func_name, response={"error": "Function not found"}
                                ))
                            )

                    # Check for Loop Death
                    if consecutive_failures >= 3:
                        print("🚨 Too many failures. Forcing FALLBACK MODE.")
                        response = self._send_message_with_retry(
                            chat, 
                            "SYSTEM: Tool failures detected. STOP using tools. SWITCH TO FALLBACK PROTOCOL IMMEDIATELY. Generate best-effort JSON now."
                        )
                        continue

                    # Send results back
                    response = self._send_message_with_retry(chat, tool_responses)
                    continue

                # [3] HANDLE TEXT RESPONSE (Extract JSON)
                if combined_text:
                    # Clean up 'THOUGHT:' for JSON parsing
                    # We strip everything before the first '{' for safety
                    json_candidate = extract_json(combined_text)

                    if is_valid_json(json_candidate):
                        print("✅ Valid JSON Final Output.")
                        return AgentResponse(json_candidate, chat.history)
                    
                    else:
                        print("⚠️  Invalid JSON. Triggering Self-Correction (Max 2 Attempts)...")
                        
                        # Attempt 1
                        response = self._send_message_with_retry(
                            chat, 
                            f"SYSTEM: Output invalid JSON. Error: SyntaxError. \nReturn ONLY the JSON object. No thoughts. \n\nInvalid Output:\n{json_candidate[:200]}..."
                        )
                        
                        # Verify Attempt 1
                        if response.candidates:
                            retry_text = response.candidates[0].content.parts[0].text
                            retry_json = extract_json(retry_text)
                            if is_valid_json(retry_json):
                                print("✅ JSON Repaired on Attempt 1.")
                                return AgentResponse(retry_json, chat.history)
                                
                        # Attempt 2 (Last Resort)
                        response = self._send_message_with_retry(
                            chat,
                            "SYSTEM: STILL INVALID. STOP. Just output empty JSON template: {\"agent_response\": \"Error...\", \"products\": []}"
                        )
                        if response.candidates:
                            retry_text = response.candidates[0].content.parts[0].text
                            retry_json = extract_json(retry_text)
                            if is_valid_json(retry_json):
                                return AgentResponse(retry_json, chat.history)

                        # Logic failed -> Hard Fallback
                        print("❌ JSON Repair Failed. Returning Hard Fallback.")
                        fallback_json = json.dumps({
                            "agent_response": combined_text.replace('"', "'")[:800],
                            "products": [],
                            "predictive_insight": "System Note: Response layout might be imperfect."
                        })
                        return AgentResponse(fallback_json, chat.history)

                # [4] HANDLE STOP REASONS
                if finish_reason in [1, 2, 3, 4, 5]:
                    print(f"⚠️ Stopped early: {finish_reason}")
                    return AgentResponse(
                        json.dumps({"agent_response": f"I couldn't finish (Code {finish_reason}). Please try again.", "products": []}), 
                        chat.history
                    )

            # Max Iterations Reached
            print("🛑 Max iterations reached.")
            return AgentResponse(
                 json.dumps({"agent_response": "I apologize, but I timed out. Please try a simpler request.", "products": []}), 
                 chat.history
            )

        except Exception as e:
            print(f"🔥 Critical Agent Error: {e}")
            return AgentResponse(
                json.dumps({"agent_response": f"Internal Error: {str(e)}", "products": []}), 
                chat_history
            )


class AgentResponse:
    def __init__(self, output, chat_history):
        self.output = output
        self.chat_history = chat_history
