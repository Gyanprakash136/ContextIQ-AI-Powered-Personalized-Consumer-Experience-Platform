
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Cannot find GOOGLE_API_KEY")
    exit(1)

genai.configure(api_key=api_key)

print("List of available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
