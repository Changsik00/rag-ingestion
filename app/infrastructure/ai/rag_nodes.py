"""
RAG Graph의 각 노드 비즈니스 로직을 캡슐화한 클래스.

각 노드는 RAGGraphState를 입력받아 필요한 필드를 업데이트하고
업데이트된 State를 반환합니다.

Spec 033: LangGraph State Management
Design Guide 005: 3-Layer Architecture (Brain → Nervous System → Body)
"""

import asyncio
import re
from typing import Any, TYPE_CHECKING


from typing import Any, TYPE_CHECKING
from langchain_core.runnables import RunnableConfig

from app.core.logger import setup_logger
from app.domain.services.intent_classifier import IntentClassifier
from app.domain.services.prompts.reranker import RERANKER_PROMPT
from app.domain.services.query_rewriter import QueryRewriter
from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.intent import IntentType, UserIntent
from app.domain.value_objects.rag_state import RAGGraphState

logger = setup_logger(__name__)


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

    def _extract_text_content(self, content: Any) -> str:
        """
        Gemini 3.0 Multimodal Response Parsing Helper.
        - List[Part] 형태에서 Text Part만 추출하여 결합합니다.
        - Non-text objects (images, blobs) are skipped.
        """
        if isinstance(content, str):
            return content
        
        if isinstance(content, list):
            text_parts = []
            for part in content:
                # Check for 'text' attribute (LangChain MessageContent or similar)
                if hasattr(part, "text"):
                    text_parts.append(part.text)
                elif isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                     text_parts.append(part["text"])
                # Ignore other types (e.g. dicts without text, blobs) to prevent chaotic noise
            return "".join(text_parts)
            
        return str(content)

    async def classify_intent(self, state: RAGGraphState) -> RAGGraphState:
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
            # Service is now async
            user_intent = await self.intent_classifier.classify(query, history)
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}. Falling back to GENERAL_QUERY.")
            user_intent = UserIntent(
                intent=IntentType.GENERAL_QUERY, targets=[], reasoning="Fallback due to classification error"
            )

        # Query Rewriting (Service is now async)
        rewritten_query = await self.query_rewriter.rewrite(query, history)

        # Update State
        state["user_intent"] = user_intent
        state["rewritten_query"] = rewritten_query

        # [Spec 034] Reasoning Log
        reasoning_log = state.get("reasoning_log", [])
        reasoning_log.append(
            f"🧠 [Intent] Classified as {user_intent.intent.value} targeting {user_intent.targets}. Reasoning: {user_intent.reasoning}"
        )
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

    async def retrieve_hybrid(self, state: RAGGraphState, config: RunnableConfig) -> RAGGraphState:
        """
        Node 3: Hybrid Search (Memory/Body Layer)

        Parallel로 Vector, Keyword, Graph 검색을 수행하고 결과를 State에 저장합니다.
        각 리포지토리는 동기식으로 구현되어 있으므로 asyncio.to_thread를 사용하여 병렬로 실행합니다.

        Args:
            state: RAGGraphState
            config: LangGraph Config (retrieval_config 포함)

        Returns:
            RAGGraphState with updated vector_chunks, keyword_chunks, graph_data
        """
        rewritten_query = state.get("rewritten_query") or state["query"]
        user_intent = state.get("user_intent")
        final_filters = state.get("final_filters")

        # Spec 055: Advanced Settings
        retrieval_config = config.get("configurable", {}).get("retrieval_config", {})
        top_k = retrieval_config.get("top_k", 5)
        strategy = retrieval_config.get("search_strategy", "hybrid")

        # [Spec 044] Extract entities for Graph Search
        entities = getattr(user_intent, "entities", []) if user_intent else []

        # [Spec 034] Initial Search reasoning
        reasoning_log = state.get("reasoning_log", [])
        
        tasks = []
        # Strategy Logic
        if strategy in ["hybrid", "vector"]:
            tasks.append(asyncio.to_thread(self._search_vector, rewritten_query, top_k, final_filters))
        else:
            tasks.append(asyncio.to_thread(lambda: []))  # Empty task

        if strategy in ["hybrid", "keyword"]:
            tasks.append(asyncio.to_thread(self._search_keyword, rewritten_query, top_k, final_filters))
        else:
            tasks.append(asyncio.to_thread(lambda: []))

        # Graph Search is always enabled unless restricted? Keeping it enabled.
        tasks.append(asyncio.to_thread(self._search_graph, rewritten_query, entities))

        logger.info(f"RAG Retrieval: query='{rewritten_query}', filters={final_filters}, entities={entities}, strategy={strategy}, top_k={top_k}")
        
        results = await asyncio.gather(*tasks)
        vector_results = results[0]
        keyword_results = results[1]
        graph_results = results[2]

        reasoning_log.append(
            f"🔍 [Search] Strategy: {strategy}, Top-K: {top_k}. Found {len(vector_results)} vector chunks, {len(keyword_results)} keyword chunks, {len(graph_results)} graph facts."
        )

        # Fallback Logic: 필터링된 결과가 없고 필터가 적용된 상태라면 필터 제거 후 재검색
        # Fallback only if the active strategy yielded nothing?
        active_results_count = len(vector_results) + len(keyword_results)
        
        if final_filters and active_results_count == 0:
            logger.info("No results found with filters. Triggering Fallback (Global Search)...")
            state["fallback_triggered"] = True
            reasoning_log.append(
                "🔄 [Fallback] Strict filters returned zero results. Retrying with Global Search (no filters)."
            )

            # 재검색 (필터 없이) - Respect Strategy
            fb_tasks = []
            if strategy in ["hybrid", "vector"]:
                fb_tasks.append(asyncio.to_thread(self._search_vector, rewritten_query, top_k, None))
            else:
                fb_tasks.append(asyncio.to_thread(lambda: []))

            if strategy in ["hybrid", "keyword"]:
                fb_tasks.append(asyncio.to_thread(self._search_keyword, rewritten_query, top_k, None))
            else:
                fb_tasks.append(asyncio.to_thread(lambda: []))
            
            fb_results = await asyncio.gather(*fb_tasks)
            vector_results = fb_results[0]
            keyword_results = fb_results[1]

            reasoning_log.append(
                f"🔍 [Search/Fallback] Post-fallback found {len(vector_results)} vector chunks, {len(keyword_results)} keyword chunks."
            )

        # [Spec 037] Context Noise Cleaning
        # 검색된 각 청크의 내용에 대해 전처리를 수행합니다.
        for i, chunk in enumerate(vector_results):
            vector_results[i] = chunk.model_copy(update={"content": self._clean_context_noise(chunk.content)})

        for i, chunk in enumerate(keyword_results):
            keyword_results[i] = chunk.model_copy(update={"content": self._clean_context_noise(chunk.content)})

        # Update State
        state["vector_chunks"] = vector_results
        state["keyword_chunks"] = keyword_results
        state["graph_data"] = graph_results
        state["reasoning_log"] = reasoning_log

        return state

    async def rerank_results(self, state: RAGGraphState, config: RunnableConfig) -> RAGGraphState:
        """
        Node 3.5: LLM Reranker (Body Layer - Precision Refinement)

        검색된 청크들을 LLM을 사용하여 다시 평가하고, 관련성이 높은 청크들만 남깁니다.
        [Spec 048] 구현.

        Args:
            state: RAGGraphState

        Returns:
            RAGGraphState with updated reranked_chunks and rerank_log
        """
        query = state["query"]
        rewritten_query = state.get("rewritten_query") or query
        vector_chunks = state.get("vector_chunks", [])
        keyword_chunks = state.get("keyword_chunks", [])

        # Combine and interleave to ensure diversity in reranking candidates
        # Keyword matches are often higher precision but lower recall than vector
        all_chunks = []
        seen_ids = set()

        # Interleave pattern: K1, V1, K2, V2...
        max_len = max(len(vector_chunks), len(keyword_chunks))
        for i in range(max_len):
            if i < len(keyword_chunks):
                c = keyword_chunks[i]
                if c.id not in seen_ids:
                    all_chunks.append(c)
                    seen_ids.add(c.id)
            if i < len(vector_chunks):
                c = vector_chunks[i]
                if c.id not in seen_ids:
                    all_chunks.append(c)
                    seen_ids.add(c.id)

        if not all_chunks:
            logger.warning(f"No chunks found to rerank for query: {rewritten_query}")
            state["reranked_chunks"] = []
            return state

        # [Spec 048] Pointwise Reranking
        # 상위 15개로 확장하여 키워드 매칭 결과가 충분히 포함되도록 함
        rerank_targets = all_chunks[:15]

        # Spec 055: Configuration for Reranker
        retrieval_config = config.get("configurable", {}).get("retrieval_config", {})
        temperature = retrieval_config.get("temperature", 0.0)

        rerank_log = []
        rerank_tasks = []

        for chunk in rerank_targets:
            prompt = RERANKER_PROMPT.format(query=rewritten_query, chunk_text=chunk.content)
            rerank_tasks.append(self._get_rerank_score(chunk, prompt, temperature))

        # Run 리랭킹 in parallel
        rerank_results = await asyncio.gather(*rerank_tasks)

        # [Spec 048] Filter by threshold
        # Lowered to 3 to keep contextually useful chunks (e.g. artist info)
        min_relevance_score = 3
        final_reranked = []

        for chunk, score_data in zip(rerank_targets, rerank_results):
            score = score_data.get("score", 0)
            reasoning = score_data.get("reasoning", "No reasoning")

            rerank_log.append({"chunk_id": chunk.id, "score": score, "reasoning": reasoning})

            if score >= min_relevance_score:
                chunk.metadata["rerank_score"] = score  # Store for citation prioritization
                final_reranked.append(chunk)

        # Sort by score descending
        final_reranked.sort(key=lambda x: x.metadata.get("rerank_score", 0), reverse=True)

        state["reranked_chunks"] = final_reranked
        state["rerank_log"] = rerank_log

        # Update Reasoning Log
        reasoning_log = state.get("reasoning_log", [])
        reasoning_log.append(
            f"🎯 [Rerank] Filtered {len(all_chunks)} chunks down to {len(final_reranked)} based on LLM relevance scores."
        )
        state["reasoning_log"] = reasoning_log

        return state

    async def _get_rerank_score(self, chunk: Chunk, prompt: str, temperature: float = 0.0) -> dict:
        """LLM을 호출하여 청크의 관련성 점수를 가져옵니다."""
        import json

        try:
            # Propagate temperature to reranker
            llm = self.llm.bind(temperature=temperature)
            response = await llm.agenerate(prompt)
            if hasattr(response, "content"):
                 content = self._extract_text_content(response.content)
            else:
                content = str(response)

            # JSON block 추출 (LLM이 마크다운 형식을 포함할 수 있음)
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Reranking failed for chunk {chunk.id}: {e}")
            return {"score": 0, "reasoning": f"Error: {e}"}

    def _clean_context_noise(self, text: str) -> str:
        """
        [Spec 037] RAG 컨텍스트 노이즈 제거.
        Wikipedia Navbox, Infobox, 파일 링크 등 답변 생성에 방해되는 요소를 제거합니다.
        """
        if not text:
            return ""

        # 1. Wikipedia Infobox (Keep content for role/title/etc.)
        # We remove generic templates but try to preserve Infobox data by hiding the wrapper but keeping internal lines
        # Or more simply, avoid greedy match for just anything {{...}}.
        # Here we ignore Navbox and Cite but keep Infobox.
        text = re.sub(r"\{\|.*?\|\}", "", text, flags=re.DOTALL)  # Wiki Tables

        # Remove Navbox, Cite, and other noise templates, but EXEMPT Infobox
        # Using a lookahead to avoid matching {{Infobox
        text = re.sub(r"\{\{(?!(?:Infobox|정보상자)).*?\}\}", "", text, flags=re.DOTALL)

        # 2. Wikipedia File/Image links
        text = re.sub(r"\[\[파일:.*?\]\]", "", text)
        text = re.sub(r"\[\[File:.*?\]\]", "", text)

        # 3. Excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 4. Empty markdown tables (e.g. | | |)
        text = re.sub(r"\|[\s\|-]+\|\n", "", text)

        return text.strip()

    async def generate_answer(self, state: RAGGraphState, config: RunnableConfig) -> RAGGraphState:
        """
        Node 4: Answer Generation

        검색 결과를 포맷팅하고 LLM을 사용하여 최종 답변을 생성합니다.

        Args:
            state: RAGGraphState
            config: LangGraph Config (retrieval_config 포함)

        Returns:
            RAGGraphState with updated full_context and final_answer
        """
        query = state["query"]
        rewritten_query = state.get("rewritten_query") or query
        vector_chunks = state.get("vector_chunks", [])
        keyword_chunks = state.get("keyword_chunks", [])
        reranked_chunks = state.get("reranked_chunks")
        graph_data = state.get("graph_data", [])
        
        # Spec 055: Configuration
        retrieval_config = config.get("configurable", {}).get("retrieval_config", {})
        temperature = retrieval_config.get("temperature", 0.0)

        # Use reranked_chunks if available, otherwise fallback to original chunks
        # [Spec 048] Dynamic Context Window
        target_chunks = reranked_chunks if reranked_chunks is not None else (vector_chunks + keyword_chunks)

        # Format Context
        context_str, mapped_chunks = self._merge_and_format_context(target_chunks, [], graph_data)

        # Spec 055: Conditional Strictness
        strict_rag_instruction = ""
        if temperature < 0.1:
            strict_rag_instruction = (
                "CRITICAL: STRICT RAG MODE ENABLED (Temperature 0).\n"
                "1. If the 'Provided Context (DB)' is empty or irrelevant, you MUST say 'I cannot find relevant information in the uploaded documents.'\n"
                "2. DO NOT answer from your internal knowledge regarding the specific subject of the question.\n"
                "3. ONLY use internal knowledge for language translation or explaining general terms mentioned IN the context.\n"
            )

        prompt = (
            "You are a professional AI assistant. Answer the question using ONLY the provided Context (DB) as your primary source.\n\n"
            f"{strict_rag_instruction}"
            "KNOWLEDGE MIXING RULES:\n"
            "1. PRIORITIZE KNOWLEDGE GRAPH: The 'Graph Facts' section contains high-precision structured relationships. Treat these as the most reliable source of truth.\n"
            "2. PRIORITIZE DOCUMENT CONTEXT: If information is not in the Graph, use 'Document Context'. It MUST be prioritized over your internal knowledge.\n"
            "3. CITATION REQUIREMENT: For every sentence or fact derived from the Document Context, you MUST append the corresponding source ID in brackets, e.g., [1] or [2][3].\n"
            "4. INTERNAL KNOWLEDGE LIMITATION: Use your internal knowledge ONLY to bridge small gaps or provide basic context (e.g. definitions). Do NOT introduce major facts that are not in the DB if the temperature is 0.\n"
            "5. NO CITATION FOR INTERNAL KNOWLEDGE: Do NOT append any brackets or source IDs for information derived from your internal knowledge.\n\n"
            f"Question: {query}\n"
            f"(Rewritten Query for Search): {rewritten_query}\n\n"
            "=== Provided Context (DB) ===\n"
            f"{context_str}\n\n"
            "Answer:"
        )

        # [Spec 048] Async LLM Refactoring
        # Apply temperature dynamically
        llm = self.llm.bind(temperature=temperature)
        response = await llm.ainvoke(prompt)

        if hasattr(response, "content"):
            answer_text = self._extract_text_content(response.content)
        else:
            answer_text = str(response)

        # [Spec 035] Citation Parsing
        # Answer 내의 [n] 패턴을 찾아 실제 메타데이터와 매칭
        indices = [int(idx_str) for idx_str in re.findall(r"\[(\d+)\]", answer_text)]
        citations = []
        seen_indices = set()
        for idx in indices:
            if idx in mapped_chunks and idx not in seen_indices:
                chunk = mapped_chunks[idx]
                citations.append(
                    {
                        "index": idx,
                        "source": chunk.metadata.get("source", "Unknown"),
                        "title": chunk.metadata.get("title", "Untitled"),
                        "url": chunk.metadata.get("url") or chunk.metadata.get("source_url"),
                    }
                )
                seen_indices.add(idx)

        # Update State
        state["full_context"] = context_str
        state["citations"] = citations
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

    def _search_vector(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        """Vector DB(ChromaDB) MMR 검색 (Sync)"""
        return self.chroma_repo.search_mmr(query, limit=limit, filters=filters)

    def _search_keyword(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        """Neo4j Keyword 검색 (Sync)"""
        return self.neo4j_doc_repo.search(query, limit=limit, filters=filters)

    def _search_graph(self, query: str, entities: list[str] | None = None) -> list[dict]:
        """Neo4j Graph Traversal (Sync)"""
        # [Spec 044] Entity Based Search
        if entities and len(entities) > 0:
            return self.neo4j_graph_repo.find_shortest_path(entities)

        # Fallback: Keyword-based Subgraph (Legacy)
        return self.neo4j_graph_repo.get_subgraph([query])

    def _merge_and_format_context(
        self, vector_chunks: list[Chunk], keyword_chunks: list[Chunk], graph_data: list[dict]
    ) -> tuple[str, dict[int, Chunk]]:
        """
        검색 결과를 병합하고 포맷팅하여 LLM에게 제공할 Context를 생성합니다.
        Citations(출처)를 포함하여 Hallucination 방지.

        Returns:
            tuple: (포맷팅된 컨텍스트 문자열, 인덱스별 Chunk 매핑 딕셔너리)
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
        mapped_chunks = {}
        for i, chunk in enumerate(combined, 1):
            source = chunk.metadata.get("source", "Unknown")
            title = chunk.metadata.get("title", "Untitled")
            formatted_chunks.append(f"[{i}] Source: {source} ({title})\n{chunk.content}")
            mapped_chunks[i] = chunk

        text_context = "\n\n".join(formatted_chunks)

        # Format Graph Context
        graph_lines = []
        if graph_data:
            graph_lines.append("Graph Facts:")
            for item in graph_data:
                src = item.get("source")
                rel = item.get("relationship")
                tgt = item.get("target")

                # Filter out MENTIONS (Internal link metadata) and None values
                if rel == "MENTIONS" or not src or not tgt or src == "None" or tgt == "None":
                    continue

                graph_lines.append(f"- ({src}) -[{rel}]-> ({tgt})")

        graph_context = "\n".join(graph_lines)

        return f"{graph_context}\n\nDocument Context:\n{text_context}", mapped_chunks
