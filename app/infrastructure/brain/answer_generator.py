import re
from typing import Any

from langchain_core.runnables import RunnableConfig

from app.domain.value_objects.chunk import Chunk


class AnswerGenerator:
    """
    Brain Layer Component: Generates the final answer based on the retrieved context and user query.
    Synthesizes information and ensures correctness through citation and knowledge mixing rules.
    """

    def __init__(self, llm: Any):
        self.llm = llm

    async def generate_answer(
        self,
        query: str,
        rewritten_query: str,
        context_str: str,
        config: RunnableConfig,
        temperature: float = 0.0,
    ) -> str:
        """
        Generates answer using LLM.
        """
        # [Spec 055] Conditional Strictness & Relaxed Mode
        strict_rag_instruction = ""
        primary_source_instruction = "Answer the question using ONLY the provided Context (DB) as your primary source."
        internal_knowledge_rule = "4. INTERNAL KNOWLEDGE LIMITATION: Use your internal knowledge ONLY to bridge small gaps or provide basic context (e.g. definitions). Do NOT introduce major facts that are not in the DB if the temperature is 0."

        if temperature < 0.1:
            strict_rag_instruction = (
                "CRITICAL: STRICT RAG MODE ENABLED (Temperature 0).\n"
                "1. Answer using ONLY the provided 'Provided Context (DB)'.\n"
                "2. If the context contains relevant information, synthesize it carefully.\n"
                "3. If the context is COMPLETELY irrelevant or does not contain the answer, you MUST say: 'I cannot find relevant information in the uploaded documents to answer this question.'\n"
                "4. DO NOT use your internal knowledge for facts NOT present in the provided context.\n"
                "5. DO NOT hallucinate or try to find flimsy associations with famous names if they are not relevant to the query.\n"
            )
        elif temperature >= 0.5:
            # Relaxed Mode
            primary_source_instruction = "Answer the question using the provided Context (DB) as your primary source. If the context is insufficient, you MAY use your internal knowledge to provide a helpful answer."
            internal_knowledge_rule = "4. INTERNAL KNOWLEDGE ALLOWED: You are encouraged to use your internal knowledge to answer the question if the Provided Context is missing or insufficient. However, still prioritize the Context if it is relevant."

        prompt = (
            f"You are a professional AI assistant. {primary_source_instruction}\n\n"
            f"{strict_rag_instruction}"
            "KNOWLEDGE MIXING RULES:\n"
            "1. PRIORITIZE KNOWLEDGE GRAPH: The 'Graph Facts' section contains high-precision structured relationships. Treat these as the most reliable source of truth.\n"
            "2. PRIORITIZE DOCUMENT CONTEXT: If information is not in the Graph, use 'Document Context'. It MUST be prioritized over your internal knowledge.\n"
            "3. CITATION REQUIREMENT: For every sentence or fact derived from the Document Context, you MUST append the corresponding source ID in brackets, e.g., [1] or [2][3].\n"
            f"{internal_knowledge_rule}\n"
            "5. NO CITATION FOR INTERNAL KNOWLEDGE: Do NOT append any brackets or source IDs for information derived from your internal knowledge.\n\n"
            f"Question: {query}\n"
            f"(Rewritten Query for Search): {rewritten_query}\n\n"
            "=== Provided Context (DB) ===\n"
            f"{context_str}\n\n"
            "Answer:"
        )

        # Apply temperature dynamically
        llm = self.llm.bind(temperature=temperature)
        response = await llm.ainvoke(prompt, config=config)

        if hasattr(response, "content"):
            return str(response.content)
        else:
            return str(response)

    def format_context(
        self,
        vector_chunks: list[Chunk],
        keyword_chunks: list[Chunk],
        graph_data: list[dict],
        reranked_chunks: list[Chunk] | None = None
    ) -> tuple[str, dict[int, Chunk]]:
        """
        Formats retrieved chunks and graph data into a context string.
        """
        # Usage priority: Reranked > Combined(Vector+Keyword)
        target_chunks = vector_chunks + keyword_chunks
        if reranked_chunks is not None:
            target_chunks = reranked_chunks

        combined = []
        seen_ids = set()

        for c in target_chunks:
            if c.id not in seen_ids:
                combined.append(c)
                seen_ids.add(c.id)

        # Format Text Context
        formatted_chunks = []
        mapped_chunks = {}
        for i, chunk in enumerate(combined, 1):
            source = chunk.metadata.get("source", "Unknown")
            title = chunk.metadata.get("title", "Untitled")
            # Truncate content for display if needed
            formatted_chunks.append(f"[{i}] Source: {source} ({title})\n{chunk.content}")
            mapped_chunks[i] = chunk

        text_context = "\n\n".join(formatted_chunks)

        # Format Graph Context
        graph_context = ""
        if graph_data:
            graph_lines = ["Graph Facts:"]
            for fact in graph_data:
                s = fact.get("source") or "Unknown"
                r = fact.get("relationship") or "related to"
                t = fact.get("target") or "Unknown"

                # Filter out MENTIONS (Internal link metadata) and None values
                if r == "MENTIONS" or str(s) == "None" or str(t) == "None":
                    continue

                # Simple formatting
                graph_lines.append(f"- ({s}) -[{r}]-> ({t})")

            if len(graph_lines) > 1:
                graph_context = "\n".join(graph_lines)

        full_context = f"{graph_context}\n\nDocument Context:\n{text_context}"
        return full_context.strip(), mapped_chunks

    def parse_citations(self, answer_text: str, mapped_chunks: dict[int, Chunk]) -> list[dict]:
        """
        Parses [n] citations from the answer text and maps them to chunk metadata.
        """
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

        return citations
