from typing import Any, Protocol, runtime_checkable

from app.domain.value_objects.intent import UserIntent


@runtime_checkable
class IBrainService(Protocol):
    """Interface for Brain Service coordinating intent and rewriting."""
    async def classify_and_rewrite(self, query: str, history: list[dict]) -> tuple[UserIntent, str]:
        ...

@runtime_checkable
class IReranker(Protocol):
    """Interface for Reranking retrieved chunks."""
    async def rerank(self, query: str, chunks: Any, strategy: str = "pointwise", config: Any = None) -> tuple[list[Any], list[dict]]:
        ...

@runtime_checkable
class IAnswerGenerator(Protocol):
    """Interface for generating final answers based on context."""
    async def generate_answer(self, query: str, rewritten_query: str, context_str: str, config: Any, temperature: float = 0.0) -> str:
        ...

    def format_context(self, vector_chunks: list[Any], keyword_chunks: list[Any], graph_chunks: list[dict], reranked_chunks: list[Any] | None = None) -> tuple[str, dict]:
        ...

    def parse_citations(self, answer: str, context_map: dict) -> list[dict]:
        ...
