import asyncio
import logging
from typing import Any

from app.domain.value_objects.chunk import Chunk

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Retrieval Layer Service: Handles Hybrid Search (Vector + Keyword + Graph).
    Focuses solely on 'Finding' relevant information.
    """

    def __init__(
        self,
        neo4j_doc_repo: Any,
        neo4j_graph_repo: Any,
        chroma_repo: Any,
    ):
        self.neo4j_doc_repo = neo4j_doc_repo
        self.neo4j_graph_repo = neo4j_graph_repo
        self.chroma_repo = chroma_repo

    async def hybrid_search(
        self,
        query: str,
        filters: dict | None,
        strategy: str = "hybrid",
        top_k: int = 5,
        entities: list[str] | None = None,
    ) -> tuple[list[Chunk], list[Chunk], list[dict]]:
        """
        Executes hybrid search across multiple repositories in parallel.
        """
        tasks = []

        # 1. Vector Search Task
        if strategy in ["hybrid", "vector"]:
            tasks.append(asyncio.to_thread(self._search_vector, query, top_k, filters))
        else:
            tasks.append(asyncio.to_thread(lambda: []))

        # 2. Keyword Search Task
        if strategy in ["hybrid", "keyword"]:
            tasks.append(asyncio.to_thread(self._search_keyword, query, top_k, filters))
        else:
            tasks.append(asyncio.to_thread(lambda: []))

        # 3. Graph Search Task
        if strategy in ["hybrid", "graph"]:
            tasks.append(asyncio.to_thread(self._search_graph, query, entities))
        else:
            tasks.append(asyncio.to_thread(lambda: []))

        logger.info(
            f"RetrievalService: query='{query}', filters={filters}, entities={entities}, strategy={strategy}, top_k={top_k}"
        )

        results = await asyncio.gather(*tasks)
        vector_results = results[0]
        keyword_results = results[1]
        graph_results = results[2]

        # Context Noise Cleaning
        from app.core.text_cleaner import clean_context_noise

        vector_results = [
            c.model_copy(update={"content": clean_context_noise(c.content)})
            for c in vector_results
        ]
        keyword_results = [
            c.model_copy(update={"content": clean_context_noise(c.content)})
            for c in keyword_results
        ]

        return vector_results, keyword_results, graph_results

    # === Internal Search Helpers ===

    def _search_vector(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        return self.chroma_repo.search_mmr(query, limit=limit, filters=filters)

    def _search_keyword(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        return self.neo4j_doc_repo.search(query, limit=limit, filters=filters)

    def _search_graph(self, query: str, entities: list[str] | None = None) -> list[dict]:
        if entities and len(entities) > 0:
            return self.neo4j_graph_repo.find_shortest_path(entities)
        return self.neo4j_graph_repo.get_subgraph([query])

