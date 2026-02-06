import asyncio
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.infrastructure.factories.llm_factory import LLMFactory
from app.infrastructure.ai.rag_nodes import RAGNodes
from app.domain.value_objects.chunk import Chunk

async def diagnose_retrieval_and_rerank(query: str):
    print(f"\n=== Diagnostics for Query: '{query}' ===\n")
    
    # 1. Similarity Distance Measurement
    print("--- 1. ChromaDB Similarity Audit ---")
    chroma_repo = ChromaVectorRepository()
    
    # Raw query to see distances
    results = chroma_repo.collection.query(
        query_texts=[query],
        n_results=10,
        include=["documents", "distances", "metadatas"]
    )
    
    candidates = []
    if results and results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            doc = results["documents"][0][i]
            dist = results["distances"][0][i]
            meta = results["metadatas"][0][i]
            cid = results["ids"][0][i]
            
            print(f"[{i+1}] Distance: {dist:.4f} | ID: {cid} | Title: {meta.get('title', 'N/A')}")
            print(f"    Snippet: {doc[:100]}...")
            
            candidates.append(Chunk(
                id=cid,
                content=doc,
                metadata=meta,
                parent_id=meta.get("parent_id"),
                index=int(meta.get("index", 0))
            ))

    # 2. Temperature Effect Test on Reranker
    print("\n--- 2. Temperature Effect Audit ---")
    llm = LLMFactory.get_llm_adapter()
    # Manual prompt construction similar to RerankNode
    prompt_template = """너는 검색 결과의 관련성을 평가하는 전문가야.
질문과 문서의 내용을 비교하여 관련성 점수(0~10)와 간단한 이유를 JSON 형식으로 답변해줘.

질문: {query}
문서 내용: {content}

응답 형식:
{{"score": 7, "reasoning": "이유..."}}
"""

    temperatures = [0.0, 0.5, 1.0]
    
    for temp in temperatures:
        print(f"\n>> Testing Temperature: {temp}")
        # Test against the top candidate (which we think is noise)
        if candidates:
            target = candidates[0]
            prompt = prompt_template.format(query=query, content=target.content)
            
            # Re-bind temperature if supported or recreate
            bound_llm = llm.bind(temperature=temp)
            try:
                # We fixed agenerate recently to not take config
                response_text = await bound_llm.agenerate(prompt)
                print(f"   Response: {response_text.strip()}")
            except Exception as e:
                print(f"   Error: {e}")

if __name__ == "__main__":
    query = "어쩌다 어른에 대해서 알려줘"
    asyncio.run(diagnose_retrieval_and_rerank(query))
