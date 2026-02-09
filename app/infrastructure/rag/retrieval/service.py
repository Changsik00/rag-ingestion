import asyncio
import logging
import re
from typing import Any

from langchain_core.runnables import RunnableConfig

from app.core.config import get_settings
from app.domain.services.prompts.listwise_reranker import LISTWISE_RERANKER_PROMPT
from app.domain.services.prompts.reranker import RERANKER_PROMPT
from app.domain.services.prompts.reranker_v2 import RERANKER_PROMPT_V2
from app.domain.value_objects.chunk import Chunk

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Retrieval Layer Service: Handles Hybrid Search (Vector + Keyword + Graph) and Reranking.
    Accesses Infrastructure repositories directly.
    """

    def __init__(
        self,
        neo4j_doc_repo: Any,
        neo4j_graph_repo: Any,
        chroma_repo: Any,
        llm: Any,
    ):
        self.neo4j_doc_repo = neo4j_doc_repo
        self.neo4j_graph_repo = neo4j_graph_repo
        self.chroma_repo = chroma_repo
        self.llm = llm

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
        vector_results = [
            c.model_copy(update={"content": self._clean_context_noise(c.content)}) 
            for c in vector_results
        ]
        keyword_results = [
            c.model_copy(update={"content": self._clean_context_noise(c.content)}) 
            for c in keyword_results
        ]

        return vector_results, keyword_results, graph_results

    async def rerank(
        self,
        query: str,
        chunks: list[Chunk],
        strategy: str = "pointwise",
        config: RunnableConfig | None = None,
    ) -> tuple[list[Chunk], list[dict]]:
        """
        Reranks the given chunks using the specified strategy (pointwise or listwise).
        """
        if not chunks:
            return [], []

        if strategy == "listwise":
            return await self._rerank_listwise(query, chunks, config)
        
        return await self._rerank_pointwise(query, chunks, config)

    # === Internal Search Helpers ===

    def _search_vector(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        return self.chroma_repo.search_mmr(query, limit=limit, filters=filters)

    def _search_keyword(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        return self.neo4j_doc_repo.search(query, limit=limit, filters=filters)

    def _search_graph(self, query: str, entities: list[str] | None = None) -> list[dict]:
        if entities and len(entities) > 0:
            return self.neo4j_graph_repo.find_shortest_path(entities)
        return self.neo4j_graph_repo.get_subgraph([query])

    # === Internal Rerank Helpers ===

    async def _rerank_pointwise(
        self, query: str, all_chunks: list[Chunk], config: RunnableConfig | None
    ) -> tuple[list[Chunk], list[dict]]:
        
        retrieval_config = config.get("configurable", {}).get("retrieval_config", {}) if config else {}
        temperature = retrieval_config.get("temperature", 0.0)

        # Limit candidates
        rerank_targets = all_chunks[:15]
        rerank_log = []
        rerank_tasks = []

        settings = get_settings()
        reranker_prompt = RERANKER_PROMPT_V2 if settings.RERANKER_VERSION == "v2" else RERANKER_PROMPT

        for chunk in rerank_targets:
            prompt = reranker_prompt.format(query=query, chunk_text=chunk.content)
            rerank_tasks.append(self._get_rerank_score(chunk, prompt, temperature))

        rerank_results = await asyncio.gather(*rerank_tasks)
        
        min_relevance_score = 3
        final_reranked = []

        for chunk, score_data in zip(rerank_targets, rerank_results):
            score = score_data.get("score", 0)
            reasoning = score_data.get("reasoning", "No reasoning")
            status = "passed" if score >= min_relevance_score else "dropped"
            
            content_snippet = chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content
            
            rerank_log.append({
                "chunk_id": chunk.id,
                "score": score,
                "reasoning": reasoning,
                "status": status,
                "content": content_snippet,
                "source": chunk.metadata.get("source", "Unknown"),
            })

            if score >= min_relevance_score:
                chunk.metadata["rerank_score"] = score
                final_reranked.append(chunk)

        final_reranked.sort(key=lambda x: x.metadata.get("rerank_score", 0), reverse=True)
        return final_reranked, rerank_log

    async def _rerank_listwise(
        self, query: str, all_chunks: list[Chunk], config: RunnableConfig | None
    ) -> tuple[list[Chunk], list[dict]]:
        
        retrieval_config = config.get("configurable", {}).get("retrieval_config", {}) if config else {}
        temperature = retrieval_config.get("temperature", 0.0)
        
        rerank_targets = all_chunks[:10]
        expanded_targets = []
        
        # Context Expansion
        for chunk in rerank_targets:
            expanded_content = await self._expand_context_window(chunk)
            expanded_chunk = chunk.model_copy(update={"content": expanded_content})
            expanded_targets.append(expanded_chunk)

        chunks_text_list = []
        for i, chunk in enumerate(expanded_targets):
            chunks_text_list.append(f"ID: {chunk.id}\nContent: {chunk.content}")

        chunks_list_str = "\n\n---\n\n".join(chunks_text_list)
        prompt = LISTWISE_RERANKER_PROMPT.format(query=query, chunks_list=chunks_list_str)

        rerank_log = []
        final_reranked = []

        try:
            llm = self.llm.bind(temperature=temperature)
            content = await llm.agenerate(prompt)
            
            import json
            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                rankings = json.loads(json_match.group())
            else:
                rankings = json.loads(content)

            chunk_map = {c.id: c for c in rerank_targets}
            min_relevance_score = 3
            
            for item in rankings:
                chunk_id = item.get("chunk_id")
                score = item.get("score", 0)
                reasoning = item.get("reasoning", "No reasoning")
                
                if chunk_id in chunk_map:
                    chunk = chunk_map[chunk_id]
                    status = "passed" if score >= min_relevance_score else "dropped"
                    content_snippet = chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content
                    
                    rerank_log.append({
                        "chunk_id": chunk_id,
                        "score": score,
                        "reasoning": reasoning,
                        "status": status,
                        "content": content_snippet,
                        "source": chunk.metadata.get("source", "Unknown"),
                    })

                    if score >= min_relevance_score:
                        chunk.metadata["rerank_score"] = score
                        final_reranked.append(chunk)

            final_reranked.sort(key=lambda x: x.metadata.get("rerank_score", 0), reverse=True)
            return final_reranked, rerank_log

        except Exception as e:
            logger.error(f"Listwise reranking failed: {e}")
            # Fallback to pointwise
            return await self._rerank_pointwise(query, all_chunks, config)

    async def _get_rerank_score(self, chunk: Chunk, prompt: str, temperature: float = 0.0) -> dict:
        import json
        try:
            llm = self.llm.bind(temperature=temperature)
            content = await llm.agenerate(prompt)
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Reranking failed for chunk {chunk.id}: {e}")
            return {"score": 0, "reasoning": f"Error: {e}"}

    async def _expand_context_window(self, chunk: Chunk, window_size: int = 1) -> str:
        try:
            parent_id = chunk.parent_id
            if not parent_id:
                return chunk.content

            adjacent = await asyncio.to_thread(
                self.neo4j_doc_repo.get_adjacent_chunks, parent_id=parent_id, index=chunk.index, window_size=window_size
            )

            if not adjacent:
                return chunk.content

            combined_content = ""
            for adj in adjacent:
                if adj.index == chunk.index:
                    combined_content += f"\n[Pivotal Context Start]\n{adj.content}\n[Pivotal Context End]\n"
                else:
                    combined_content += adj.content + "\n"

            return combined_content.strip()
        except Exception as e:
            logger.warning(f"Failed to expand context for chunk {chunk.id}: {e}")
            return chunk.content

    def _clean_context_noise(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"\{\|.*?\|\}", "", text, flags=re.DOTALL)
        text = re.sub(r"\{\{(?!(?:Infobox|정보상자)).*?\}\}", "", text, flags=re.DOTALL)
        text = re.sub(r"\[\[파일:.*?\]\]", "", text)
        text = re.sub(r"\[\[File:.*?\]\]", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\|[\s\|-]+\|\n", "", text)
        return text.strip()
