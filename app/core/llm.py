from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.infrastructure.llm import LangChainLLMAdapter


class LLMFactory:
    @staticmethod
    @lru_cache
    def get_google_llm(model: str = "gemini-2.0-flash-exp", temperature: float = 0.0) -> ChatGoogleGenerativeAI:
        settings = get_settings()
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=api_key)

    @staticmethod
    @lru_cache
    def get_llm_adapter(model: str = "gemini-2.0-flash-exp", temperature: float = 0.0) -> LangChainLLMAdapter:
        """LangChain Adapter 반환 (LLMInterface 구현체)"""
        llm = LLMFactory.get_google_llm(model, temperature)
        return LangChainLLMAdapter(llm)


def get_llm() -> LangChainLLMAdapter:
    """Adapter 반환 (DI용)"""
    return LLMFactory.get_llm_adapter()
