
import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from app.domain.entities.chunk import Chunk
from app.domain.schemas.intent import UserIntent, IntentType
from app.domain.services.intent_classifier import IntentClassifier
from app.domain.services.query_rewriter import QueryRewriter

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    answer: str
    rewritten_query: str
    vector_chunks: list[Chunk]
    keyword_chunks: list[Chunk]
    graph_data: list[dict]
    full_context: str

class RAGService:
    def __init__(
        self,
        neo4j_doc_repo: Any,
        neo4j_graph_repo: Any,
        chroma_repo: Any,
        query_rewriter: QueryRewriter,
        intent_classifier: IntentClassifier,
        llm: Any
    ):
        """
        Orchestrates the Hybrid Retrieval Augmented Generation pipeline.
        
        Args:
            neo4j_doc_repo: Repository for Neo4j Keyword Search.
            neo4j_graph_repo: Repository for Graph Traversal.
            chroma_repo: Repository for Vector MMR Search.
            query_rewriter: Service to rewrite user queries based on history.
            intent_classifier: Service to classify user intent and extract targets.
            llm: Language Model interface (e.g., LangChain Runnable or Adapter).
        """
        self.neo4j_doc_repo = neo4j_doc_repo
        self.neo4j_graph_repo = neo4j_graph_repo
        self.chroma_repo = chroma_repo
        self.query_rewriter = query_rewriter
        self.intent_classifier = intent_classifier
        self.llm = llm

    async def retrieve_and_generate(self, query: str, history: list[dict], filters: dict | None = None) -> RAGResult:
        """
        Executes the full RAG pipeline: Intent -> Rewrite -> Hybrid Search -> Format -> Generate.
        """
        # 1. Intent Classification (NEW in Spec 032)
        user_intent = self._classify_intent_with_fallback(query, history)
        
        # 2. Convert Intent to Filters (Auto-derived)
        auto_filters = self._intent_to_filters(user_intent)
        
        # 3. Merge Filters (Manual filters override auto filters)
        final_filters = filters if filters is not None else auto_filters
        
        # 4. Rewrite Query
        rewritten_query = self.query_rewriter.rewrite(query, history)

        # 5. Parallel Hybrid Search
        vector_task = asyncio.create_task(self._search_vector(rewritten_query, final_filters))
        keyword_task = asyncio.create_task(self._search_keyword(rewritten_query, final_filters))
        graph_task = asyncio.create_task(self._search_graph(rewritten_query))

        vector_results, keyword_results, graph_results = await asyncio.gather(
            vector_task, keyword_task, graph_task
        )

        # 6. Merge and Format Context
        context_str = self._merge_and_format_context(
            vector_results, keyword_results, graph_results
        )

        # 7. Generate Answer
        prompt = (
            f"Please answer the following question based on the context provided below.\\n\\n"
            f"Question: {query}\\n"
            f"(Context/Rewritten): {rewritten_query}\\n\\n"
            f"Context:\\n{context_str}\\n\\n"
            f"Answer:"
        )

        response = self.llm.generate(prompt)

        if hasattr(response, 'content'):
            answer_text = response.content
        else:
            answer_text = str(response)

        return RAGResult(
            answer=answer_text,
            rewritten_query=rewritten_query,
            vector_chunks=vector_results,
            keyword_chunks=keyword_results,
            graph_data=graph_results,
            full_context=context_str
        )

    def _classify_intent_with_fallback(self, query: str, history: list[dict]) -> UserIntent:
        """
        Intent Classification with Graceful Degradation.
        LLM 파싱 실패 시 GENERAL_QUERY로 Fallback.
        """
        try:
            return self.intent_classifier.classify(query, history)
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}. Falling back to GENERAL_QUERY.")
            return UserIntent(
                intent=IntentType.GENERAL_QUERY,
                targets=[],
                reasoning="Fallback due to classification error"
            )

    def _intent_to_filters(self, intent: UserIntent) -> dict | None:
        """
        Intent를 Repository Filters로 변환.
        
        Args:
            intent: User Intent 분류 결과
            
        Returns:
            dict: Repository 필터 (document_id, topic 등)
            None: 필터 불필요 (GENERAL_QUERY)
        """
        if intent.intent == IntentType.COMPARE or intent.intent == IntentType.SUMMARIZE:
            # targets를 document_id 또는 source 필터로 변환
            # 실제 구현에서는 targets를 document ID로 매핑하는 로직 필요
            if intent.targets:
                # 간단한 구현: targets를 lowercase로 변환하여 source 검색
                return {"source": intent.targets}
            return None
        
        elif intent.intent == IntentType.FILTER_BY_TOPIC:
            # targets를 topic/entity 필터로 변환
            if intent.targets:
                return {"topic": intent.targets}
            return None
        
        else:  # GENERAL_QUERY
            return None

    async def _search_vector(self, query: str, filters: dict | None = None) -> list[Chunk]:
        return self.chroma_repo.search_mmr(query, filters=filters)

    async def _search_keyword(self, query: str, filters: dict | None = None) -> list[Chunk]:
        return self.neo4j_doc_repo.search(query, filters=filters)

    async def _search_graph(self, query: str) -> list[dict]:
        return self.neo4j_graph_repo.get_subgraph([query])

    def _merge_and_format_context(
        self,
        vector_chunks: list[Chunk],
        keyword_chunks: list[Chunk],
        graph_data: list[dict]
    ) -> str:
        """
        Merges chunks, deduplicates, and formats citations.
        Adds Graph Facts at the top.
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
            formatted_chunks.append(
                f"[{i}] Source: {source} ({title})\\n{chunk.content}"
            )

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
