import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
# Ensure API key is set - although it should be set by main.py or vector_db already
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-pro")

def generate_future_insight(current_product_category: str):
    """
    Predicts a future need based on a current purchase.
    Input: Category of item (e.g., 'Gaming Laptop', 'Puppy Crate').
    Output: A string advice.
    """
    try:
        response = model.generate_content(
            f"""
            Based on the user's interest in {current_product_category}, generate a short predictive insight about what they might need in 1-3 months.
            Focus on accessories, maintenance, or complementary items.
            Format: "Prediction: Since you are buying X, you might need Y soon because Z."
            Keep it under 2 sentences.
            """
        )
        return response.text
    except Exception as e:
        # Fallback if AI fails
        insights = {
            "laptop": "Prediction: You will likely need a USB-C Hub and Screen Cleaner in 2 months.",
            "shoes": "Prediction: High mileage runners often need replacement insoles after 3 months.",
            "camera": "Prediction: 4K video fills storage fast. You will need a V90 SD Card soon."
        }
        for key in insights:
            if key in current_product_category.lower():
                return insights[key]
        return "Prediction: Consider adding a warranty or protection plan for long-term care."