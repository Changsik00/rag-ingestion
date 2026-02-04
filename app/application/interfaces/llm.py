from typing import Any, Protocol

from app.domain.value_objects.extracted_metadata import ExtractedMetadata


class LLMInterface(Protocol):
    """
    LLM 추상 인터페이스 - Domain 레이어용

    Python Protocol을 사용하여 Duck Typing 기반 인터페이스 정의.
    구체적 구현체는 Infrastructure 레이어에서 제공.


    주로 메타데이터 추출 및 텍스트 생성에 사용됨.
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

    async def cleanup_thread(self, thread_id: str) -> None:
        """스레드 히스토리 정리 (Cleanup)"""
        ...


class LLMInvoker(Protocol):
    """
    LLM Invoker 인터페이스 - LangChain 호환용


    LangChain의 ChatModel 인터페이스와 호환되는 Protocol.
    주로 Factory나 범용 LLM 호출에 사용됨.
    """

    async def ainvoke(self, messages: Any) -> Any:
        """Asynchronously invoke the LLM with messages (LangChain compatibility)"""
        ...

    def invoke(self, messages: Any) -> Any:
        """Synchronously invoke the LLM with messages (LangChain compatibility)"""
        ...
