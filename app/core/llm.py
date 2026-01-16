from typing import Optional
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class LLMFactory:
    @staticmethod
    @lru_cache()
    def get_google_llm(model: str = "gemini-2.0-flash-exp", temperature: float = 0.0) -> ChatGoogleGenerativeAI:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key
        )

def get_llm() -> ChatGoogleGenerativeAI:
    return LLMFactory.get_google_llm()
