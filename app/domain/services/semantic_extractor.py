import logging

from app.domain.interfaces.llm import LLMInterface
from app.domain.schemas.extraction import ExtractedMetadata

logger = logging.getLogger(__name__)


class SemanticExtractor:
    """
    도메인 서비스: 텍스트 메타데이터 추출 오케스트레이션

    외부 프레임워크(LangChain 등)에 독립적인 순수 비즈니스 로직.
    구체적인 LLM 구현은 Infrastructure 레이어에서 주입.
    """

    def __init__(self, llm: LLMInterface):
        """
        Args:
            llm: LLM 인터페이스 구현체 (Infrastructure에서 주입)
        """
        self.llm = llm

    async def extract(self, text: str, thread_id: str | None = None) -> ExtractedMetadata | None:
        """
        텍스트에서 메타데이터 추출

        Args:
            text: 분석할 텍스트
            thread_id: Optional thread ID for persistence (HITL)

        Returns:
            ExtractedMetadata: 추출된 메타데이터 (실패 시 None)
        """
        if hasattr(self.llm, "extract_metadata"):
            try:
                # adapter methods are now async
                import asyncio
                if asyncio.iscoroutinefunction(self.llm.extract_metadata):
                    return await self.llm.extract_metadata(text, thread_id=thread_id)
                else:
                    return self.llm.extract_metadata(text, thread_id=thread_id)
            except TypeError:
                # Fallback for other adapters
                if asyncio.iscoroutinefunction(self.llm.extract_metadata):
                    return await self.llm.extract_metadata(text)
                else:
                    return self.llm.extract_metadata(text)
        return None
