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

    async def run_pipeline(
        self, 
        query: str, 
        history: list[dict], 
        config: RunnableConfig,
        manual_filters: dict | None = None
    ) -> dict:
        """
        Executes the complete RAG pipeline.
        Returns a dictionary representing the final state (similar to RAGGraphState).
        """
        state = {
            "query": query, 
            "history": history, 
            "manual_filters": manual_filters,
            "reasoning_log": []
        }

        # 1. Brain: Intent Classification & Query Rewriting
        user_intent, rewritten_query = await self.brain.classify_and_rewrite(query, history)
        state["user_intent"] = user_intent
        state["rewritten_query"] = rewritten_query
        
        # 2. Orchestration: Filter Routing
        filters = await self._route_filters(user_intent, manual_filters, state)
        state["final_filters"] = filters

        # 3. Retrieval: Hybrid Search
        # Retrieve config
        retrieval_config = config.get("configurable", {}).get("retrieval_config", {})
        top_k = retrieval_config.get("top_k", 5)
        strategy = retrieval_config.get("search_strategy", "hybrid")
        
        # Extract entities for graph search
        entities = getattr(user_intent, "targets", []) # Should be entities if distinct, but using targets as fallback
        if hasattr(user_intent, "entities"):
             entities = user_intent.entities

        vector_chunks, keyword_chunks, graph_data = await self.retrieval.hybrid_search(
            rewritten_query,
            filters=filters,
            strategy=strategy,
            top_k=top_k,
            entities=entities
        )
        
        state["vector_chunks"] = vector_chunks
        state["keyword_chunks"] = keyword_chunks
        state["graph_data"] = graph_data
        
        state["reasoning_log"].append(
            f"🔍 [Search] Strategy: {strategy}, Top-K: {top_k}. Found {len(vector_chunks)} vector, {len(keyword_chunks)} keyword, {len(graph_data)} graph facts."
        )

        # 4. Orchestration: Fallback Handling (If empty results with filters)
        active_results_count = len(vector_chunks) + len(keyword_chunks)
        if filters and active_results_count == 0:
            logger.info("No results found with filters. Triggering Fallback (Global Search)...")
            state["fallback_triggered"] = True
            state["reasoning_log"].append("🔄 [Fallback] Strict filters returned zero results. Retrying with Global Search.")
            
            # Retry without filters
            vector_chunks, keyword_chunks, _ = await self.retrieval.hybrid_search(
                rewritten_query,
                filters=None,
                strategy=strategy,
                top_k=top_k,
                entities=entities
            )
            state["vector_chunks"] = vector_chunks
            state["keyword_chunks"] = keyword_chunks
            
            state["reasoning_log"].append(
                f"🔍 [Search/Fallback] Found {len(vector_chunks)} vector, {len(keyword_chunks)} keyword."
            )

        # 5. Brain: Reranking
        all_chunks = vector_chunks + keyword_chunks
        # Deduplicate by ID before reranking
        unique_chunks_map = {c.id: c for c in all_chunks}
        unique_chunks = list(unique_chunks_map.values())
        
        reranked_chunks, rerank_log = await self.reranker.rerank(
            rewritten_query, 
            unique_chunks, 
            strategy="pointwise", # Could be dynamic based on config
            config=config
        )
        state["reranked_chunks"] = reranked_chunks
        state["rerank_log"] = rerank_log
        
        state["reasoning_log"].append(
            f"🎯 [Rerank] Passed {len(reranked_chunks)} / {len(unique_chunks)} chunks."
        )

        # 6. Brain: Answer Generation
        # Format Context
        context_str, mapped_chunks = self.answer_generator.format_context(
            vector_chunks, keyword_chunks, graph_data, reranked_chunks
        )
        state["full_context"] = context_str
        
        # Generate Answer
        temperature = retrieval_config.get("temperature", 0.0)
        answer_text = await self.answer_generator.generate_answer(
            query, rewritten_query, context_str, config, temperature
        )
        state["final_answer"] = answer_text
        
        # Parse Citations
        citations = self.answer_generator.parse_citations(answer_text, mapped_chunks)
        state["citations"] = citations

        return state

    async def _route_filters(self, intent: UserIntent, manual_filters: dict | None, state: dict) -> dict | None:
        """
        Converts UserIntent to Repository Filters.
        Includes Logic for Fuzzy Matching (if enabled).
        """
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
