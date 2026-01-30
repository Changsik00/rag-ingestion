import asyncio
import os
import json
from app.interfaces.api.dependencies import get_rag_service
from app.domain.entities.rag import RAGQuery

async def test_rag():
    print("Testing RAG Pipeline...")
    rag_service = get_rag_service()
    
    query = RAGQuery(
        question="네오사피엔스 주식매수선택권 계약의 행사가격은 얼마인가요?",
        conversation_id="test-session"
    )
    
    print(f"Querying: {query.question}")
    result = await rag_service.retrieve_and_generate(query)
    
    print("\n--- Answer ---")
    print(result.answer)
    print("\n--- Sources ---")
    for doc in result.sources:
        print(f"- {doc.title} (ID: {doc.id})")
    
    if "500원" in result.answer:
        print("\n✅ Verification Successful: Correct price found!")
    else:
        print("\n❌ Verification Failed: Could not find the correct price in the answer.")

if __name__ == "__main__":
    # We need to set up the environment for the script if running via uv run
    asyncio.run(test_rag())
