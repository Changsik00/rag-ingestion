"""
RAG Graph의 각 노드 비즈니스 로직을 캡슐화한 클래스.

각 노드는 RAGGraphState를 입력받아 필요한 필드를 업데이트하고
업데이트된 State를 반환합니다.

Spec 033: LangGraph State Management
Design Guide 005: 3-Layer Architecture (Brain → Nervous System → Body)
"""

import asyncio
import logging
from typing import Any

from app.domain.entities.chunk import Chunk
from app.domain.rag.state import RAGGraphState
from app.domain.schemas.intent import IntentType, UserIntent
from app.domain.services.intent_classifier import IntentClassifier
from app.domain.services.query_rewriter import QueryRewriter

logger = logging.getLogger(__name__)


class RAGNodes:
    """
    RAG Pipeline의 각 Graph Node 비즈니스 로직을 구현하는 클래스.
    
    각 메서드는 LangGraph 노드로 사용되며,
    RAGGraphState를 입력받아 업데이트된 State를 반환합니다.
    """

    def __init__(
        self,
        neo4j_doc_repo: Any,
        neo4j_graph_repo: Any,
        chroma_repo: Any,
        query_rewriter: QueryRewriter,
        intent_classifier: IntentClassifier,
        llm: Any,
    ):
        """
        Args:
            neo4j_doc_repo: Neo4j Document Repository (Keyword Search)
            neo4j_graph_repo: Neo4j Graph Repository (Traversal)
            chroma_repo: ChromaDB Repository (Vector MMR Search)
            query_rewriter: Query Rewriting Service
            intent_classifier: Intent Classification Service
            llm: Language Model Interface
        """
        self.neo4j_doc_repo = neo4j_doc_repo
        self.neo4j_graph_repo = neo4j_graph_repo
        self.chroma_repo = chroma_repo
        self.query_rewriter = query_rewriter
        self.intent_classifier = intent_classifier
        self.llm = llm

    def classify_intent(self, state: RAGGraphState) -> RAGGraphState:
        """
        Node 1: Intent Classification + Query Rewriting (Brain Layer)
        
        사용자 질문의 의도를 분석하고, 대화 이력을 반영하여 질문을 재작성합니다.
        
        Args:
            state: RAGGraphState
            
        Returns:
            RAGGraphState with updated user_intent and rewritten_query
        """
        query = state["query"]
        history = state["history"]

        # Intent Classification (with Fallback)
        try:
            user_intent = self.intent_classifier.classify(query, history)
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}. Falling back to GENERAL_QUERY.")
            user_intent = UserIntent(
                intent=IntentType.GENERAL_QUERY,
                targets=[],
                reasoning="Fallback due to classification error"
            )

        # Query Rewriting
        rewritten_query = self.query_rewriter.rewrite(query, history)

        # Update State
        state["user_intent"] = user_intent
        state["rewritten_query"] = rewritten_query

        # [Spec 034] Reasoning Log
        reasoning_log = state.get("reasoning_log", [])
        reasoning_log.append(f"🧠 [Intent] Classified as {user_intent.intent.value} targeting {user_intent.targets}. Reasoning: {user_intent.reasoning}")
        reasoning_log.append(f"✍️ [Rewrite] Query rewritten to: {rewritten_query}")
        state["reasoning_log"] = reasoning_log

        return state

    def route_decision(self, state: RAGGraphState) -> RAGGraphState:
        """
        Node 2: Intent → Filters 변환 (Nervous System Layer)
        
        Intent Classifier의 결정을 Repository Filters로 변환하고,
        Manual Filters와 병합합니다 (Manual Filters가 우선).
        
        Args:
            state: RAGGraphState
            
        Returns:
            RAGGraphState with updated auto_filters and final_filters
        """
        user_intent = state.get("user_intent")
        manual_filters = state.get("manual_filters")

        # Convert Intent to Auto Filters
        auto_filters = self._intent_to_filters(user_intent) if user_intent else None

        # Merge Filters (Manual > Auto)
        final_filters = manual_filters if manual_filters is not None else auto_filters

        # Update State
        state["auto_filters"] = auto_filters
        state["final_filters"] = final_filters
        state["fallback_triggered"] = False

        # [Spec 034] Reasoning Log
        reasoning_log = state.get("reasoning_log", [])
        filter_desc = f"Applied Filters: {final_filters}" if final_filters else "No Filters Applied"
        reasoning_log.append(f"🚦 [Routing] {filter_desc}")
        state["reasoning_log"] = reasoning_log

        return state

    async def retrieve_hybrid(self, state: RAGGraphState) -> RAGGraphState:
        """
        Node 3: Hybrid Search (Memory/Body Layer)
        
        Parallel로 Vector, Keyword, Graph 검색을 수행하고 결과를 State에 저장합니다.
        각 리포지토리는 동기식으로 구현되어 있으므로 asyncio.to_thread를 사용하여 병렬로 실행합니다.
        
        Args:
            state: RAGGraphState
            
        Returns:
            RAGGraphState with updated vector_chunks, keyword_chunks, graph_data
        """
        rewritten_query = state.get("rewritten_query") or state["query"]
        final_filters = state.get("final_filters")

        # [Spec 034] Initial Search reasoning
        reasoning_log = state.get("reasoning_log", [])

        # Parallel Hybrid Search (Running sync calls in threads)
        vector_task = asyncio.to_thread(self._search_vector, rewritten_query, final_filters)
        keyword_task = asyncio.to_thread(self._search_keyword, rewritten_query, final_filters)
        graph_task = asyncio.to_thread(self._search_graph, rewritten_query)

        vector_results, keyword_results, graph_results = await asyncio.gather(
            vector_task, keyword_task, graph_task
        )

        reasoning_log.append(f"🔍 [Search] Found {len(vector_results)} vector chunks, {len(keyword_results)} keyword chunks, {len(graph_results)} graph facts.")

        # Fallback Logic: 필터링된 결과가 없고 필터가 적용된 상태라면 필터 제거 후 재검색
        if final_filters and not vector_results and not keyword_results:
            logger.info("No results found with filters. Triggering Fallback (Global Search)...")
            state["fallback_triggered"] = True
            reasoning_log.append("🔄 [Fallback] Strict filters returned zero results. Retrying with Global Search (no filters).")

            # 재검색 (필터 없이)
            v_fallback_task = asyncio.to_thread(self._search_vector, rewritten_query, None)
            k_fallback_task = asyncio.to_thread(self._search_keyword, rewritten_query, None)

            v_fall, k_fall = await asyncio.gather(v_fallback_task, k_fallback_task)
            vector_results = v_fall
            keyword_results = k_fall

            reasoning_log.append(f"🔍 [Search/Fallback] Post-fallback found {len(vector_results)} vector chunks, {len(keyword_results)} keyword chunks.")

        # Update State
        state["vector_chunks"] = vector_results
        state["keyword_chunks"] = keyword_results
        state["graph_data"] = graph_results
        state["reasoning_log"] = reasoning_log

        return state

    def generate_answer(self, state: RAGGraphState) -> RAGGraphState:
        """
        Node 4: Answer Generation
        
        검색 결과를 포맷팅하고 LLM을 사용하여 최종 답변을 생성합니다.
        
        Args:
            state: RAGGraphState
            
        Returns:
            RAGGraphState with updated full_context and final_answer
        """
        query = state["query"]
        rewritten_query = state.get("rewritten_query") or query
        vector_chunks = state.get("vector_chunks", [])
        keyword_chunks = state.get("keyword_chunks", [])
        graph_data = state.get("graph_data", [])

        # Format Context
        context_str = self._merge_and_format_context(vector_chunks, keyword_chunks, graph_data)

        # Generate Answer
        prompt = (
            "You are a professional AI assistant. Answer the question based strictly on the provided Context.\n"
            "CRITICAL RULES:\n"
            "1. If the provided context is empty or does not contain sufficient information to answer the question, "
            "explicitly state that you do not have enough information in your knowledge base to answer definitively.\n"
            "2. Do NOT use your internal knowledge to supplement the answer if it's not supported by the context.\n"
            "3. If multiple documents are provided, cite them correctly using [Source ID].\n\n"
            f"Question: {query}\n"
            f"(Rewritten Query): {rewritten_query}\n\n"
            f"Context:\n{context_str}\n\n"
            "Answer:"
        )

        response = self.llm.generate(prompt)

        if hasattr(response, "content"):
            answer_text = response.content
        else:
            answer_text = str(response)

        # Update State
        state["full_context"] = context_str
        state["final_answer"] = answer_text

        return state

    # === Helper Methods ===

    def _intent_to_filters(self, intent: UserIntent | None) -> dict | None:
        """
        Intent를 Repository Filters로 변환.
        
        Args:
            intent: User Intent 분류 결과
            
        Returns:
            dict: Repository 필터 (source, topic 등)
            None: 필터 불필요 (GENERAL_QUERY)
        """
        if not intent:
            return None

        if intent.intent == IntentType.COMPARE or intent.intent == IntentType.SUMMARIZE:
            # targets를 source 필터로 변환
            if intent.targets:
                return {"source": intent.targets}
            return None

        elif intent.intent == IntentType.FILTER_BY_TOPIC:
            # targets를 topic 필터로 변환
            if intent.targets:
                return {"topic": intent.targets}
            return None

        else:  # GENERAL_QUERY
            return None

    def _search_vector(self, query: str, filters: dict | None = None) -> list[Chunk]:
        """Vector DB(ChromaDB) MMR 검색 (Sync)"""
        return self.chroma_repo.search_mmr(query, filters=filters)

    def _search_keyword(self, query: str, filters: dict | None = None) -> list[Chunk]:
        """Neo4j Keyword 검색 (Sync)"""
        return self.neo4j_doc_repo.search(query, filters=filters)

    def _search_graph(self, query: str) -> list[dict]:
        """Neo4j Graph Traversal (Sync)"""
        return self.neo4j_graph_repo.get_subgraph([query])

    def _merge_and_format_context(
        self, vector_chunks: list[Chunk], keyword_chunks: list[Chunk], graph_data: list[dict]
    ) -> str:
        """
        검색 결과를 병합하고 포맷팅하여 LLM에게 제공할 Context를 생성합니다.
        Citations(출처)를 포함하여 Hallucination 방지.
        """
        combined = []
        seen_ids = set()

        def add_chunks(chunks):
            for c in chunks:
                if c.id not in seen_ids:
                    combined.append(c)
                    seen_ids.add(c.id)

        add_chunks(vector_chunks)
        add_chunks(keyword_chunks)

        # Format Text Context
        formatted_chunks = []
        for i, chunk in enumerate(combined, 1):
            source = chunk.metadata.get("source", "Unknown")
            title = chunk.metadata.get("title", "Untitled")
            formatted_chunks.append(f"[{i}] Source: {source} ({title})\\n{chunk.content}")

        text_context = "\\n\\n".join(formatted_chunks)

        # Format Graph Context
        graph_lines = []
        if graph_data:
            graph_lines.append("Graph Facts:")
            for item in graph_data:
                src = item.get("source")
                rel = item.get("relationship")
                tgt = item.get("target")
                graph_lines.append(f"- ({src}) -[{rel}]-> ({tgt})")

        graph_context = "\\n".join(graph_lines)

        return f"{graph_context}\\n\\nDocument Context:\\n{text_context}"
