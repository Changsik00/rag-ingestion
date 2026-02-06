import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("API Key not found")
        return
    
    genai.configure(api_key=api_key)
    print("--- Available Models ---")
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"- {m.name} ({m.display_name})")

if __name__ == "__main__":
    list_models()
