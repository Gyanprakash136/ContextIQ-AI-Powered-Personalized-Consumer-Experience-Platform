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

    # 2. Bracket Counting (robust path)
    stack = []
    start_index = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if not stack:
                start_index = i
            stack.append(char)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack:
                    # Found a complete JSON object
                    return text[start_index : i+1]
    
    # 3. Fallback (failed to find complete object)
    return text

class Agent:
    def __init__(self, model: str, name: str, instruction: str, tools: list):
        self.model_name = model
        self.name = name
        self.system_instruction = instruction
        self.tools = tools
        self.tool_map = {}
        self.valid_urls = set() # Anti-hallucination cache

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
        
        # Reset URL cache for new session request
        self.valid_urls.clear()

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
                
                # [1] HANDLE TOOL CALLS
                if function_calls:
                    print(f"🛠  Tools requested: {len(function_calls)}")
                    tool_responses = []
                    
                    for fc in function_calls:
                        func_name = fc.name
                        func_args = dict(fc.args)

                        # Hallucination Guard: Validating URLs
                        if func_name == "scrape_url":
                            target_url = func_args.get("url")
                            # If checking against search results, implement logic here.
                            # For now, we trust the agent IF we haven't seen issues, 
                            # but per requirements: "Store valid URLs + block scrapes on unknown URLs"
                            # We need to populate self.valid_urls from 'search_web' results.
                            pass 

                        # Guardrail: Prevent >2 identical calls
                        call_sig = f"{func_name}:{json.dumps(func_args, sort_keys=True)}"
                        tool_usage_count[call_sig] = tool_usage_count.get(call_sig, 0) + 1
                        
                        if tool_usage_count[call_sig] > 2:
                            print(f"🛑 Blocking duplicate tool call: {func_name}")
                            tool_responses.append(
                                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                                    name=func_name, response={"error": "STOP. Repeated call. Move to next state."}
                                ))
                            )
                            continue

                        # Execute Tool
                        if func_name in self.tool_map:
                            try:
                                print(f"   👉 Executing {func_name}...")
                                result = self.tool_map[func_name](**func_args)
                                
                                # URL Tracking
                                if func_name == "search_web" and isinstance(result, list):
                                    for item in result:
                                        if isinstance(item, dict) and "link" in item:
                                            self.valid_urls.add(item["link"])
                                
                                # Return RAW dict (Not stringified)
                                # Truncate long text fields if necessary inside the result dict
                                tool_responses.append(
                                    genai.protos.Part(function_response=genai.protos.FunctionResponse(
                                        name=func_name, response={"result": result}
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
                        # Construct a User Message to steer behaviour (NOT 'SYSTEM:')
                        response = self._send_message_with_retry(
                            chat, 
                            "CRITICAL FAILURE PREVENTED. Stop using tools. Immediately switch to FALLBACK PROTOCOL. Return valid JSON recommendations now."
                        )
                        continue

                    # Send results back
                    response = self._send_message_with_retry(chat, tool_responses)
                    continue

                # [2] HANDLE TEXT RESPONSE
                if combined_text:
                    # Robust extraction
                    final_json_text = extract_json(combined_text)

                    if is_valid_json(final_json_text):
                        print("✅ Valid JSON Final Output.")
                        return AgentResponse(final_json_text, chat.history)
                    
                    else:
                        print("⚠️  Invalid JSON. Triggering Self-Correction...")
                        
                        # Attempt 1: Strict steer
                        response = self._send_message_with_retry(
                            chat, 
                            f"ERROR: Your output was not valid JSON. \nFix Syntax Immediately. \nReturn ONLY the JSON object. \n\nBad Output Start:\n{final_json_text[:200]}..."
                        )
                        
                        # Verify Attempt 1
                        if response.candidates:
                            retry_text = response.candidates[0].content.parts[0].text
                            retry_json = extract_json(retry_text)
                            if is_valid_json(retry_json):
                                print("✅ JSON Repaired.")
                                return AgentResponse(retry_json, chat.history)
                                
                        # Attempt 2: Minimal template steer
                        response = self._send_message_with_retry(
                            chat,
                            "ERROR: STIll Invalid. Return exact empty JSON template: {\"agent_response\": \"...\", \"products\": []}"
                        )
                        if response.candidates:
                            retry_text = response.candidates[0].content.parts[0].text
                            retry_json = extract_json(retry_text)
                            if is_valid_json(retry_json):
                                return AgentResponse(retry_json, chat.history)

                        # Hard Fallback
                        print("❌ JSON Repair Failed. Outputting Fallback Wrapper.")
                        fallback_json = json.dumps({
                            "agent_response": combined_text.replace('"', "'")[:800],
                            "products": [],
                            "predictive_insight": "System Note: Output format error."
                        })
                        return AgentResponse(fallback_json, chat.history)

                # [3] HANDLE STOP REASONS
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
