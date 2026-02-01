from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.domain.interfaces.llm import LLMInvoker
from app.infrastructure.ai.extractors.langchain_extractor import LangChainExtractor


class LLMFactory:
    """Factory for creating LLM instances"""

    """Factory for creating LLM instances"""

    @staticmethod
    @lru_cache
    def get_google_llm(model: str | None = None, temperature: float = 0.0) -> ChatGoogleGenerativeAI:
        settings = get_settings()
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        target_model = model or settings.GEMINI_MODEL_NAME
        return ChatGoogleGenerativeAI(model=target_model, temperature=temperature, google_api_key=api_key)

    @staticmethod
    @lru_cache
    def get_llm_adapter(model: str | None = None, temperature: float = 0.0) -> LLMInvoker:
        """LangChain Adapter 반환 (LLMInterface Protocol 구현체)"""
        llm = LLMFactory.get_google_llm(model, temperature)
        return LangChainExtractor(llm)


def get_llm() -> LLMInvoker:
    """Adapter 반환 (DI용)"""
    return LLMFactory.get_llm_adapter()
