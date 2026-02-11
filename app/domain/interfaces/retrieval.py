from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IRetrievalService(Protocol):
    """Interface for Hybrid Search (Vector, Keyword, Graph)."""

    async def hybrid_search(
        self,
        query: str,
        filters: dict | None = None,
        strategy: str = "hybrid",
        top_k: int = 5,
        entities: list[str] | None = None,
    ) -> tuple[list[Any], list[Any], list[dict]]: ...
