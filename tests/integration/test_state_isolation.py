import pytest
from langchain_core.messages import HumanMessage
from app.application.services.agent import ConversationalRAGAgent
from app.application.services.rag import RAG, RAGResult
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_session_state_isolation_and_override():
    """세션 내에서 두 번째 질문 시 이전 질문의 데이터가 덮어씌워지는지 검증"""
    mock_rag = MagicMock(spec=RAG)
    mock_ingestion = MagicMock()
    
    agent = ConversationalRAGAgent(rag_service=mock_rag, ingestion_service=mock_ingestion)
    
    # turn 1
    mock_rag.retrieve_and_generate = AsyncMock(return_value=RAGResult(
        answer="Jobs answer",
        rewritten_query="Jobs query",
        vector_chunks=[{"id": "jobs_chunk", "metadata": {"distance": 0.1}}],
        keyword_chunks=[],
        graph_data=[],
        full_context="Jobs context",
        rerank_log=[{"id": "jobs_log"}]
    ))
    
    state_turn1 = {
        "messages": [HumanMessage(content="Who is Steve Jobs?")],
        "intent": "search",
        "thread_id": "thread-1",
        "hitl_enabled": False,
        "filters": None
    }
    
    config = {"configurable": {"retrieval_config": {}}}
    output1 = await agent.search_node(state_turn1, config)
    
    # turn 2
    mock_rag.retrieve_and_generate = AsyncMock(return_value=RAGResult(
        answer="Adult answer",
        rewritten_query="Adult query",
        vector_chunks=[{"id": "adult_chunk", "metadata": {"distance": 0.2}}],
        keyword_chunks=[],
        graph_data=[],
        full_context="Adult context",
        rerank_log=[{"id": "adult_log"}]
    ))
    
    # state1의 결과가 포함된 상태에서 2번째 검색 수행 시뮬레이션
    state_turn2 = {
        **state_turn1,
        **output1, # 1차 결과가 들어있는 상태
        "messages": state_turn1["messages"] + [HumanMessage(content="What is 어쩌다 어른?")]
    }
    
    output2 = await agent.search_node(state_turn2, config)
    
    # 검증: vector_chunks나 rerank_log에 이전 데이터(Jobs)가 없어야 함
    assert len(output2["rerank_log"]) == 1
    assert output2["rerank_log"][0]["id"] == "adult_log"
    assert output2["context_data"]["vector_chunks"][0]["id"] == "adult_chunk"
    
    print("\n✅ Isolation Verification: Stale data was successfully overwritten by new results.")

if __name__ == "__main__":
    pass
