from typing import Protocol

from app.domain.schemas.extraction import ExtractedMetadata


class LLMInterface(Protocol):
    """
    LLM 추상 인터페이스 - Domain 레이어용

    Python Protocol을 사용하여 Duck Typing 기반 인터페이스 정의.
    구체적 구현체는 Infrastructure 레이어에서 제공.
    """

    def extract_metadata(self, text: str) -> ExtractedMetadata | None:
        """
        텍스트에서 구조화된 메타데이터 추출

        Args:
            text: 분석할 원본 텍스트

        Returns:
            ExtractedMetadata: 추출된 메타데이터 (title, summary, keywords, entities)
            None: 추출 실패 시

        Example:
            >>> llm = get_llm_implementation()
            >>> metadata = llm.extract_metadata("Sample text...")
            >>> print(metadata.title)
            "Sample Title"

        """
        ...

    def generate(self, prompt: str) -> str:
        """
        단순 텍스트 생성

        Args:
            prompt: 입력 프롬프트

        Returns:
            str: 생성된 텍스트
        """
        ...
