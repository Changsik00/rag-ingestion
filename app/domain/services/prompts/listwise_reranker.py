"""
Listwise Reranker를 위한 프롬프트 정의.
"""

LISTWISE_RERANKER_PROMPT = """
You are an expert information retriever. Your task is to analyze a set of Document Chunks and rank them based on their relevance to a given User Query.

Assign a relevance score (0-10) and a relative rank to each chunk.
- High Score (8-10): Contains direct, critical information for the answer.
- Mid Score (4-7): Provides useful context or partial information.
- Low Score (0-3): Irrelevant or noise.

Query: {query}

Chunks to Evaluate:
{chunks_list}

Provide your response in JSON format as an array of objects:
[
    {{
        "chunk_id": "<id>",
        "score": <int>,
        "rank": <int>,
        "reasoning": "<concise explanation in Korean why this chunk is ranked here>"
    }},
    ...
]
"""
