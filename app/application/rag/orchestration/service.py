import logging
import asyncio
from typing import Any

from langchain_core.runnables import RunnableConfig

from app.domain.rag.brain.service import BrainService
from app.domain.rag.brain.reranker import Reranker
from app.domain.rag.brain.answer_generator import AnswerGenerator
from app.infrastructure.rag.retrieval.service import RetrievalService
from app.domain.value_objects.intent import IntentType, UserIntent
from app.domain.value_objects.chunk import Chunk

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """
    Orchestration Layer: Coordinates the flow between Brain and Retrieval layers.
    Replaces the legacy RAGNodes class using Clean Architecture.
    """

    def __init__(
        self,
        brain_service: BrainService,
        reranker: Reranker,
        answer_generator: AnswerGenerator,
        retrieval_service: RetrievalService,
        filter_matcher: Any = None,  # Optional: For Fuzzy Matching (Spec 073)
    ):
        self.brain = brain_service
        self.reranker = reranker
        self.answer_generator = answer_generator
        self.retrieval = retrieval_service
        self.filter_matcher = filter_matcher

    async def classify(self, query: str, history: list[dict]) -> tuple[UserIntent, str]:
        """Step 1: Intent Classification & Query Rewriting"""
        return await self.brain.classify_and_rewrite(query, history)

    async def route_filters(self, intent: UserIntent, manual_filters: dict | None) -> dict | None:
        """Step 2: Filter Routing"""
        auto_filters = {}
        
        if not intent:
            return manual_filters

        # Basic intent-to-filter logic
        if intent.intent in [IntentType.COMPARE, IntentType.SUMMARIZE] and intent.targets:
             auto_filters["source"] = intent.targets
                
        elif intent.intent == IntentType.FILTER_BY_TOPIC and intent.targets:
             auto_filters["topic"] = intent.targets
                
        # Merge filters
        final_filters = {}
        if auto_filters:
            final_filters.update(auto_filters)
        if manual_filters:
            final_filters.update(manual_filters)
            
        return final_filters if final_filters else None

    async def search(
        self, 
        rewritten_query: str, 
        filters: dict | None, 
        user_intent: UserIntent, 
        config: RunnableConfig,
        logging_list: list[str] | None = None
    ) -> tuple[list[Chunk], list[Chunk], list[dict], bool]:
        """
        Step 3: Hybrid Search with Fallback
        Returns: (vector_chunks, keyword_chunks, graph_data, fallback_triggered)
        """
        retrieval_config = config.get("configurable", {}).get("retrieval_config", {})
        top_k = retrieval_config.get("top_k", 5)
        strategy = retrieval_config.get("search_strategy", "hybrid")
        
        entities = getattr(user_intent, "targets", [])
        if hasattr(user_intent, "entities"):
             entities = user_intent.entities

        vector_chunks, keyword_chunks, graph_data = await self.retrieval.hybrid_search(
            rewritten_query,
            filters=filters,
            strategy=strategy,
            top_k=top_k,
            entities=entities
        )
        
        if logging_list is not None:
            logging_list.append(
                f"🔍 [Search] Strategy: {strategy}, Top-K: {top_k}. Found {len(vector_chunks)} vector, {len(keyword_chunks)} keyword, {len(graph_data)} graph facts."
            )

        fallback_triggered = False
        active_results_count = len(vector_chunks) + len(keyword_chunks)
        
        # Fallback Logic
        if filters and active_results_count == 0:
            logger.info("No results found with filters. Triggering Fallback (Global Search)...")
            fallback_triggered = True
            
            if logging_list is not None:
                logging_list.append("🔄 [Fallback] Strict filters returned zero results. Retrying with Global Search.")
            
            vector_chunks, keyword_chunks, _ = await self.retrieval.hybrid_search(
                rewritten_query,
                filters=None,
                strategy=strategy,
                top_k=top_k,
                entities=entities
            )
            
            if logging_list is not None:
                logging_list.append(
                    f"🔍 [Search/Fallback] Found {len(vector_chunks)} vector, {len(keyword_chunks)} keyword."
                )
                
        return vector_chunks, keyword_chunks, graph_data, fallback_triggered

    async def rerank(
        self,
        rewritten_query: str,
        vector_chunks: list[Chunk],
        keyword_chunks: list[Chunk],
        config: RunnableConfig,
        logging_list: list[str] | None = None
    ) -> tuple[list[Chunk], list[dict]]:
        """Step 4: Reranking"""
        all_chunks = vector_chunks + keyword_chunks
        unique_chunks_map = {c.id: c for c in all_chunks}
        unique_chunks = list(unique_chunks_map.values())
        
        reranked_chunks, rerank_log = await self.reranker.rerank(
            rewritten_query, 
            unique_chunks, 
            strategy="pointwise", 
            config=config
        )
        
        if logging_list is not None:
            logging_list.append(
                f"🎯 [Rerank] Passed {len(reranked_chunks)} / {len(unique_chunks)} chunks."
            )
            
        return reranked_chunks, rerank_log

    async def generate(
        self,
        query: str,
        rewritten_query: str,
        vector_chunks: list[Chunk],
        keyword_chunks: list[Chunk],
        graph_data: list[dict],
        reranked_chunks: list[Chunk],
        config: RunnableConfig
    ) -> tuple[str, list[dict], str]:
        """Step 5: Answer Generation"""
        context_str, mapped_chunks = self.answer_generator.format_context(
            vector_chunks, keyword_chunks, graph_data, reranked_chunks
        )
        
        retrieval_config = config.get("configurable", {}).get("retrieval_config", {})
        temperature = retrieval_config.get("temperature", 0.0)
        
        answer_text = await self.answer_generator.generate_answer(
            query, rewritten_query, context_str, config, temperature
        )
        
        citations = self.answer_generator.parse_citations(answer_text, mapped_chunks)
        
        return answer_text, citations, context_str

    async def run_pipeline(
        self, 
        query: str, 
        history: list[dict], 
        config: RunnableConfig,
        manual_filters: dict | None = None
    ) -> dict:
        """
        Executes the complete RAG pipeline sequentially.
        """
        state = {
            "query": query, 
            "history": history, 
            "manual_filters": manual_filters,
            "reasoning_log": []
        }

        # 1. Classify
        user_intent, rewritten_query = await self.classify(query, history)
        state["user_intent"] = user_intent
        state["rewritten_query"] = rewritten_query
        
        # 2. Route
        filters = await self.route_filters(user_intent, manual_filters)
        state["final_filters"] = filters

        # 3. Search
        vector_chunks, keyword_chunks, graph_data, fallback = await self.search(
            rewritten_query, filters, user_intent, config, state["reasoning_log"]
        )
        state["vector_chunks"] = vector_chunks
        state["keyword_chunks"] = keyword_chunks
        state["graph_data"] = graph_data
        state["fallback_triggered"] = fallback

        # 4. Rerank
        reranked_chunks, rerank_log = await self.rerank(
            rewritten_query, vector_chunks, keyword_chunks, config, state["reasoning_log"]
        )
        state["reranked_chunks"] = reranked_chunks
        state["rerank_log"] = rerank_log

        # 5. Generate
        answer_text, citations, full_context = await self.generate(
            query, rewritten_query, vector_chunks, keyword_chunks, graph_data, reranked_chunks, config
        )
        state["final_answer"] = answer_text
        state["citations"] = citations
        state["full_context"] = full_context

        return state


