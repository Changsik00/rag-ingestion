"""
Reranker를 위한 프롬프트 정의.
"""

RERANKER_PROMPT = """
You are an expert information retriever. Your task is to evaluate the relevance of a Document Chunk to a given User Query.

Assign a relevance score between 1 and 10, where:
- 10: The chunk contains the EXACT answer to the query.
- 5: The chunk is highly relevant and likely contains the answer or core facts.
- 3: The chunk provide some background info (artist, date, etc.) but does NOT directly answer the question.
- 0: The chunk is irrelevant noise or unrelated to the query.

Query: {query}

Chunk:
{chunk_text}

Provide your response in JSON format:
{{
    "score": <int>,
    "reasoning": "<concise explanation in Korean>"
}}
"""
