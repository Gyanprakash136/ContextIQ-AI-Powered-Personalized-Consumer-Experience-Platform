import google.generativeai as genai
from google.generativeai.types import content_types
import json
import os
import time


def is_valid_json(text: str) -> bool:
    """Check whether a string is valid JSON."""
    try:
        json.loads(text)
        return True
    except:
        return False


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
            "HARM_CATEGORY_HARASSUREMENT": "BLOCK_NONE",
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


    def run(self, user_input, chat_history=None, max_iterations=15):
        """Main agentic loop."""
        if chat_history is None:
            chat_history = []

        chat = self.model.start_chat(
            history=chat_history,
            enable_automatic_function_calling=False
        )

        try:
            response = self._send_message_with_retry(chat, user_input)

            iteration = 0
            while iteration < max_iterations:
                iteration += 1
                print(f"Iteration {iteration}/{max_iterations}")

                if not response.candidates:
                    print("No candidates in response.")
                    break

                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason
                print(f"Finish Reason: {finish_reason}")

                function_calls = []
                text_parts = []

                # Separate text parts & function calls
                for part in candidate.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        function_calls.append(part.function_call)
                    elif hasattr(part, "text") and part.text:
                        text_parts.append(part.text)

                combined_text = "".join(text_parts).strip()

                # ------------------------------------------------------------
                # CASE 1: FUNCTION CALLS
                # ------------------------------------------------------------
                if function_calls:
                    print(f"Tool calls requested: {len(function_calls)}")

                    tool_responses = []
                    for fc in function_calls:
                        func_name = fc.name
                        func_args = dict(fc.args)
                        print(f"Calling tool: {func_name}")

                        if func_name not in self.tool_map:
                            error_msg = f"Function {func_name} not found"
                            print(error_msg)
                            tool_responses.append(
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=func_name,
                                        response={"error": error_msg}
                                    )
                                )
                            )
                            continue

                        try:
                            result = self.tool_map[func_name](**func_args)
                            tool_responses.append(
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=func_name,
                                        response={"result": json.dumps(result)}
                                    )
                                )
                            )
                        except Exception as e:
                            print(f"Error running tool {func_name}: {e}")
                            tool_responses.append(
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=func_name,
                                        response={"error": str(e)}
                                    )
                                )
                            )

                    response = self._send_message_with_retry(chat, tool_responses)
                    continue

                # ------------------------------------------------------------
                # CASE 2: TEXT RECEIVED BUT MUST VALIDATE JSON
                # ------------------------------------------------------------
                if combined_text:
                    print("Received text from model")

                    # Accept final output only if JSON is valid
                    if is_valid_json(combined_text):
                        print("Valid JSON detected. Returning final output.")
                        return AgentResponse(combined_text, chat.history)

                    # Detect weak fallback text
                    if "I couldn't access live listings" in combined_text:
                        print("Weak fallback detected. Requesting strict regeneration.")
                        response = self._send_message_with_retry(
                            chat,
                            "Your response is incomplete. Regenerate using STRICT JSON, markdown links, grouped categories, and 3–5 products per group."
                        )
                        continue

                    # If not JSON -> instruct model to output correct JSON
                    print("Text is not JSON. Requesting valid JSON only.")
                    response = self._send_message_with_retry(
                        chat,
                        "Your previous message was NOT valid JSON. Return ONLY the JSON object according to the system instructions."
                    )
                    continue

                # ------------------------------------------------------------
                # CASE 3: MODEL STOPPED EARLY
                # ------------------------------------------------------------
                if finish_reason in [1, 2, 3, 4, 5]:
                    print(f"Model stopped early (finish_reason={finish_reason})")
                    return AgentResponse(
                        output=f"I couldn't finish the response (Reason: {finish_reason}). Try again.",
                        chat_history=chat.history
                    )

            # If loop finishes without success
            print("Max iterations reached without valid JSON.")
            return AgentResponse(
                output="I couldn't complete your request. Please try again.",
                chat_history=chat.history
            )

        except Exception as e:
            print(f"Agent Error: {e}")
            return AgentResponse(
                output=f"Agent encountered an error: {str(e)}",
                chat_history=chat_history
            )


class AgentResponse:
    def __init__(self, output, chat_history):
        self.output = output
        self.chat_history = chat_history
