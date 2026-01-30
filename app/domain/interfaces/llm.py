from typing import Protocol

from app.domain.value_objects.extracted_metadata import ExtractedMetadata


class LLMInterface(Protocol):
    """
    LLM 추상 인터페이스 - Domain 레이어용

    Python Protocol을 사용하여 Duck Typing 기반 인터페이스 정의.
    구체적 구현체는 Infrastructure 레이어에서 제공.
    """

    async def aextract_metadata(self, text: str) -> ExtractedMetadata | None:
        """비동기 서버용 메타데이터 추출"""
        ...

    def generate(self, prompt: str) -> str:
        """단순 텍스트 생성 (동기)"""
        ...

    async def agenerate(self, prompt: str) -> str:
        """단순 텍스트 생성 (비동기)"""
        ...
