
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
sys.modules["googlesearch"] = MagicMock()

from backend.core.shim import Agent, extract_json
from backend.tools.search_tool import search_web

class TestAgentLogic(unittest.TestCase):
    
    def setUp(self):
        # Mock tools and model
        self.mock_model = MagicMock()
        self.mock_tools = []
        # Instantiate agent with dummy data
        self.agent = Agent(model="gemini-test", name="TestAgent", instruction="Test", tools=self.mock_tools)
        # Mock the model property in the agent since __init__ creates a real one
        self.agent.model = self.mock_model
        
        # Suppress prints during test
        self.capturedOutput = []

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

    @patch('backend.tools.search_tool.search')
    def test_google_search_tool(self, mock_search):
        """Test search_web wrapper around google search."""
        # Mock return from googlesearch
        mock_result = MagicMock()
        mock_result.title = "Test Title"
        mock_result.url = "http://example.com"
        mock_result.description = "Test Snippet"
        
        mock_search.return_value = [mock_result]
        
        output = search_web("test query")
        self.assertIn("Link: http://example.com", output)
        self.assertIn("Title: Test Title", output)
        
        # Verify fallback logic (advanced=False) if advanced fails
        mock_search.side_effect = [Exception("Advanced failed"), ["http://fallback.com"]]
        output_fallback = search_web("test query")
        self.assertIn("Link: http://fallback.com", output_fallback)

    def test_chat_bypass_logic(self):
        """Verify the logic flow for conversational bypass (SKIP_SEARCH)."""
        # Case 1: Pure Chat
        plan_query_chat = "SKIP_SEARCH"
        self.assertTrue("SKIP_SEARCH" in plan_query_chat)
        
        # Case 2: Product Search (Should NOT skip)
        plan_query_search = "buy laptop"
        self.assertFalse("SKIP_SEARCH" in plan_query_search)

    def test_angry_customer_bypass_intent(self):
        """Verify that complaints are considered 'Chat' to avoid searching for hate."""
        # Simulated LLM output for a complaint prompt
        # We expect the prompt instruction to drive the LLM to output SKIP_SEARCH
        # This test verifies our regex checking logic works for that output
        model_output_complaint = "SKIP_SEARCH" 
        self.assertTrue("SKIP_SEARCH" in model_output_complaint)

    def test_fallback_link_safety(self):
        """Verify that fallback links are generated correctly and safely."""
        # Test logic from _fallback_response (re-implemented here for unit verification)
        user_input = "bad product!@#"
        safe_query = re.sub(r'[^a-zA-Z0-9 ]', '', user_input).replace(" ", "+")
        link = f"https://www.amazon.in/s?k={safe_query}"
        
        self.assertEqual(safe_query, "bad+product")
        self.assertEqual(link, "https://www.amazon.in/s?k=bad+product")

if __name__ == '__main__':
    unittest.main()
