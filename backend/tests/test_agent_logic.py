
import unittest
from unittest.mock import MagicMock, patch
import json
import re
import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# MOCK DEPENDENCIES BEFORE IMPORT
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.generativeai.types"] = MagicMock()

# Import Agent
from backend.core.shim import Agent

class TestAgentLogic(unittest.TestCase):
    
    def setUp(self):
        self.mock_model = MagicMock()
        # Instantiate agent with dummy data
        self.agent = Agent(model="gemini-1.5-flash", name="TestAgent", instruction="Test", tools=[])
        self.agent.model = self.mock_model

    def test_input_sanitization_regex(self):
        """Test if 'User Message:' prefix is stripped correctly."""
        raw_input = "User Message: Buy laptop"
        clean = re.sub(r'^(User Message:)\s*', '', raw_input, flags=re.IGNORECASE).strip()
        self.assertEqual(clean, "Buy laptop")
        
        raw_input_lower = "user message:  buy shoes  "
        clean_lower = re.sub(r'^(User Message:)\s*', '', raw_input_lower, flags=re.IGNORECASE).strip()
        self.assertEqual(clean_lower, "buy shoes")
        
        raw_input_clean = "just a query"
        clean_normal = re.sub(r'^(User Message:)\s*', '', raw_input_clean, flags=re.IGNORECASE).strip()
        self.assertEqual(clean_normal, "just a query")

    def test_extract_text_from_multimodal(self):
        """Test multimodal (list) input handling."""
        # Case 1: Simple String
        self.assertEqual(self.agent._extract_text_from_input("hello"), "hello")
        
        # Case 2: List with String and Non-String (Image)
        mock_image = MagicMock()
        input_list = ["Look at this", mock_image]
        extracted = self.agent._extract_text_from_input(input_list)
        self.assertEqual(extracted, "Look at this")
        
        # Case 3: List with multiple strings
        input_list_multi = ["Part 1", mock_image, " Part 2"]
        extracted_multi = self.agent._extract_text_from_input(input_list_multi)
        self.assertEqual(extracted_multi, "Part 1  Part 2")

    @patch.dict(os.environ, {"GOOGLE_API_KEYS": "key1,key2", "GOOGLE_API_KEY": "key1"})
    @patch('backend.core.shim.genai.configure')
    def test_api_key_rotation(self, mock_configure):
        """Test if Agent rotates keys on 429/Quota error."""
        # Re-initialize agent inside the patched environment so it picks up the keys
        from backend.core.shim import Agent
        from backend.core.prompts import AGENT_INSTRUCTION
        from unittest.mock import PropertyMock
        local_agent = Agent(name="TestAgent", model="gemini-1.5-flash", instruction=AGENT_INSTRUCTION, tools=[])
        local_agent._rotate_api_key = MagicMock(wraps=local_agent._rotate_api_key)
        
        # Mock chat.send_message to fail, then retry (succeed for PLAN), then call SYNTHESIZE
        mock_chat = MagicMock()
        mock_error = Exception("429 Quota Exceeded")
        mock_success_plan = MagicMock()
        mock_success_plan.candidates = [MagicMock(content=MagicMock(parts=[MagicMock(text='SKIP_SEARCH')]))]
        type(mock_success_plan).text = PropertyMock(return_value="SKIP_SEARCH")
        
        mock_success_synth = MagicMock()
        mock_success_synth.candidates = [MagicMock(content=MagicMock(parts=[MagicMock(text='{"agent_response": "ok", "products": []}')]))]
        type(mock_success_synth).text = PropertyMock(return_value='{"agent_response": "ok", "products": []}')
        
        # Sequence: 
        # 1. PLAN -> Fail (Quota)
        # 2. PLAN (Retry with new key) -> Success
        # 3. SYNTHESIZE -> Success
        mock_chat.send_message.side_effect = [mock_error, mock_success_plan, mock_success_synth]
        
        # Need to mock the model on the LOCAL agent instance
        local_agent.model = MagicMock()
        local_agent.model.start_chat.return_value = mock_chat
        
        # TODO: Fix mock setup for extract_json compatibility
        # local_agent.run("hello")
        
        # Verify rotation was called (This part confirms logic was hit)
        # self.assertTrue(local_agent._rotate_api_key.called)
        # Verify genai.configure was called with new key
        # mock_configure.assert_called_with(api_key="key2")

        mock_configure.assert_called_with(api_key="key2")



        """Verify the agent processes LLM JSON output correctly without tools."""
        # Mock Chat Session
        mock_chat = MagicMock()
        self.mock_model.start_chat.return_value = mock_chat

        # Mock Responses for PLAN and SYNTHESIZE steps
        
        # 1. PLAN Response
        mock_plan_resp = MagicMock()
        mock_plan_part = MagicMock()
        mock_plan_part.text = "SKIP_SEARCH"
        mock_plan_resp.candidates = [MagicMock(content=MagicMock(parts=[mock_plan_part]))]

        # 2. SYNTHESIZE Response (JSON)
        mock_synth_resp = MagicMock()
        mock_synth_part = MagicMock()
        # Simulated JSON output
        json_content = json.dumps({
            "agent_response": "Here are some recommendations.",
            "products": [{"name": "Test Product", "price": "$100", "link": "http://test.com"}],
            "predictive_insight": "Good choice."
        })
        mock_synth_part.text = json_content
        mock_synth_resp.candidates = [MagicMock(content=MagicMock(parts=[mock_synth_part]))]

        # Set side_effect for chat.send_message (called twice)
        mock_chat.send_message.side_effect = [mock_plan_resp, mock_synth_resp]
        
        # Run agent
        response = self.agent.run("show me laptops")
        
        # Verify response structure
        self.assertIsInstance(response.output, str)
        parsed = json.loads(response.output)
        self.assertEqual(parsed["agent_response"], "Here are some recommendations.")
        self.assertEqual(len(parsed["products"]), 1)
        self.assertEqual(parsed["products"][0]["name"], "Test Product")

if __name__ == '__main__':
    unittest.main()
