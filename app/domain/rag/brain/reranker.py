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


class Reranker:
    """
    Brain Layer Component: Re-ranks retrieved chunks using LLM-based reasoning.
    Uses 'Thinking' capability to refine 'Finding' results.
    """

    def __init__(self, llm: Any, neo4j_doc_repo: Any):
        self.llm = llm
        self.neo4j_doc_repo = neo4j_doc_repo

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
