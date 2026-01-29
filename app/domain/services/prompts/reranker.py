"""
Reranker를 위한 프롬프트 정의.
"""

RERANKER_PROMPT = """
You are an expert information retriever. Your task is to evaluate the relevance of a Document Chunk to a given User Query.

Assign a relevance score between 1 and 10, where:
- 10: The chunk contains the exact answer or is highly relevant.
- 7: The chunk provides critical background info (artist, date, topic definition) that enriches the answer.
- 5: The chunk is somewhat related but lacks specific details for the answer.
- 1: The chunk is completely irrelevant noise.

Query: {query}

Chunk:
{chunk_text}

Provide your response in JSON format:
{{
    "score": <int>,
    "reasoning": "<concise explanation in Korean>"
}}
"""
