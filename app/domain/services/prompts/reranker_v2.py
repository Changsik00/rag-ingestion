"""
Reranker v2: Context-Aware 프롬프트 (PENALTY 규칙 제거)

Spec 069: Reranker Prompt Optimization
- PENALTY 규칙 제거하여 Over-filtering 해결
- Context-Aware 평가 기준 추가
- Multi-Entity Query 처리 개선
"""

RERANKER_PROMPT_V2 = """
You are an expert information retriever. Your task is to evaluate the relevance 
of a Document Chunk to a given User Query.

Assign a relevance score between 1 and 10, where:
- 10: The chunk contains the EXACT answer to the query.
- 7-9: The chunk is highly relevant and contains key information for answering the query.
- 4-6: The chunk is somewhat relevant but may lack specific details.
- 1-3: The chunk mentions related entities but doesn't help answer the query.
- 0: The chunk is completely irrelevant.

**Context-Aware Evaluation Guidelines:**

1. **Multi-Entity Queries** (e.g., "A와 B 비교"):
   - A document about A is relevant even if it doesn't mention B, and vice versa.
   - Score based on how well it explains A or B individually.
   - Example: For "SpaceX와 Tesla 비교", a document about SpaceX is highly relevant (7-9).

2. **Name Mentions**:
   - If the query asks about a person in a SPECIFIC CONTEXT (e.g., "X in TV Show Y"),
     a general biography of X is still SOMEWHAT RELEVANT (score 4-6), not irrelevant.
   - Only score 0-1 if the chunk is about a DIFFERENT person with the same name.
   - Example: For "어쩌다 어른에서 김영하", a Wikipedia bio of Kim Young-ha would be 4-6, not 0.

3. **Self-Verification**:
   - Before assigning the score, ask yourself: "Does this chunk help answer the query?"
   - If Yes → Score 4+
   - If Partially → Score 2-3
   - If No → Score 0-1

Query: {query}

Chunk:
{chunk_text}

Provide your response in JSON format:
{{
    "score": <int>,
    "reasoning": "<concise explanation in Korean>"
}}
"""
