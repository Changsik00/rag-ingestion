"""
Reranker를 위한 프롬프트 정의.
"""

RERANKER_PROMPT = """
You are an expert information retriever. Your task is to evaluate the relevance of a Document Chunk to a given User Query.

Assign a relevance score between 1 and 10, where:
- 10: The chunk contains the EXACT answer to the query.
- 5: The chunk is highly relevant and directly pertains to the question's specific context.
- 1: The chunk is weakly related (e.g. mentions the same name but in a different, unrelated context).
- 0: The chunk is completely irrelevant noise.
- PENALTY: Heavily penalize (score 1 or 0) documents that mention a FAMOUS NAME from the query but in a COMPLETELY DIFFERENT life or career context (e.g. Wikipedia bio vs TV Show guesting).

Note: Context consistency is critical. If the query asks about a person in a specific TV show, a biography of that person that does NOT mention the show should be scored 1 or 0. Hallucinating a connection just because of a name match is a FAILURE.

Query: {query}

Chunk:
{chunk_text}

Provide your response in JSON format:
{{
    "score": <int>,
    "reasoning": "<concise explanation in Korean>"
}}
"""
