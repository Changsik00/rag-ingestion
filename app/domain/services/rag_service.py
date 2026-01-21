
import asyncio
from dataclasses import dataclass
from typing import Any

from app.domain.entities.chunk import Chunk
from app.domain.services.query_rewriter import QueryRewriter


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
        llm: Any
    ):
        """
        Orchestrates the Hybrid Retrieval Augmented Generation pipeline.
        
        Args:
            neo4j_doc_repo: Repository for Neo4j Keyword Search.
            neo4j_graph_repo: Repository for Graph Traversal.
            chroma_repo: Repository for Vector MMR Search.
            query_rewriter: Service to rewrite user queries based on history.
            llm: Language Model interface (e.g., LangChain Runnable or Adapter).
        """
        self.neo4j_doc_repo = neo4j_doc_repo
        self.neo4j_graph_repo = neo4j_graph_repo
        self.chroma_repo = chroma_repo
        self.query_rewriter = query_rewriter
        self.llm = llm

    async def retrieve_and_generate(self, query: str, history: list[dict]) -> RAGResult:
        """
        Executes the full RAG pipeline: Rewrite -> Hybrid Search -> Format -> Generate.
        """
        # 1. Rewrite Query
        # QueryRewriter is synchronous
        rewritten_query = self.query_rewriter.rewrite(query, history)

        # 2. Parallel Hybrid Search
        # Vector, Keyword, Graph
        vector_task = asyncio.create_task(self._search_vector(rewritten_query))
        keyword_task = asyncio.create_task(self._search_keyword(rewritten_query))
        graph_task = asyncio.create_task(self._search_graph(rewritten_query))

        vector_results, keyword_results, graph_results = await asyncio.gather(
            vector_task, keyword_task, graph_task
        )

        # 3. Merge and Format Context
        context_str = self._merge_and_format_context(
            vector_results, keyword_results, graph_results
        )

        # 4. Generate Answer
        # Construct Prompt
        # TODO: Use a proper PromptTemplate.
        prompt = (
            f"Please answer the following question based on the context provided below.\n\n"
            f"Question: {query}\n"
            f"(Context/Rewritten): {rewritten_query}\n\n"
            f"Context:\n{context_str}\n\n"
            f"Answer:"
        )

        # Invoke LLM
        if asyncio.iscoroutinefunction(self.llm.ainvoke):
             response = await self.llm.ainvoke(prompt)
        else:
             response = self.llm.invoke(prompt)

        # Handle different response types
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

    async def _search_vector(self, query: str) -> list[Chunk]:
        # Using MMR for diversity (k=5, fetch_k=20 usually, but default params handled in repo)
        return self.chroma_repo.search_mmr(query)

    async def _search_keyword(self, query: str) -> list[Chunk]:
        return self.neo4j_doc_repo.search(query)

    async def _search_graph(self, query: str) -> list[dict]:
        # Get 1-depth subgraph related to entities in the query
        # Ideally, we extract entities first.
        # For this MVP, we pass the query string as a list item.
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

        # Helper to add unique chunks
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
                f"[{i}] Source: {source} ({title})\n{chunk.content}"
            )

        text_context = "\n\n".join(formatted_chunks)

        # Format Graph Context
        # data: [{'source': 'A', 'relationship': 'REL', 'target': 'B'}, ...]
        graph_lines = []
        if graph_data:
            graph_lines.append("Graph Facts:")
            for item in graph_data:
                src = item.get("source")
                rel = item.get("relationship")
                tgt = item.get("target")
                graph_lines.append(f"- ({src}) -[{rel}]-> ({tgt})")

        graph_context = "\n".join(graph_lines)

        return f"{graph_context}\n\nDocument Context:\n{text_context}"
