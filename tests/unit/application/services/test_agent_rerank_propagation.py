import pytest
from langchain_core.messages import HumanMessage
from app.application.services.agent import ConversationalRAGAgent
from app.application.services.rag import RAG, RAGResult
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_agent_search_node_propagates_rerank_log():
    # 1. Setup Mock RAG Service
    mock_rag = MagicMock(spec=RAG)
    mock_ingestion = MagicMock()
    
    # Mock RAGResult containing rerank_log
    mock_rerank_log = [
        {"chunk_id": "c1", "score": 5, "status": "passed", "reasoning": "Fits well"},
        {"chunk_id": "c2", "score": 1, "status": "dropped", "reasoning": "Too short"}
    ]
    
    mock_rag.retrieve_and_generate = AsyncMock(return_value=RAGResult(
        answer="Hello world",
        rewritten_query="test query",
        vector_chunks=[],
        keyword_chunks=[],
        graph_data=[],
        full_context="context",
        rerank_log=mock_rerank_log
    ))
    
    agent = ConversationalRAGAgent(rag_service=mock_rag, ingestion_service=mock_ingestion)
    
    # 2. Setup AgentState
    state = {
        "messages": [HumanMessage(content="Explain RAG")],
        "intent": "search",
        "thread_id": "test-thread",
        "hitl_enabled": False,
        "filters": None
    }
    
    # 3. Call search_node
    config = {"configurable": {"retrieval_config": {}}}
    output = await agent.search_node(state, config)
    
    # 4. Verify propagation
    assert "rerank_log" in output
    assert output["rerank_log"] == mock_rerank_log
    assert output["tool_output"] == "Search Completed"
    assert "context_data" in output
    
    print("\n✅ Internal Verification: Rerank log propagated from RAG Service to Agent Node.")

if __name__ == "__main__":
    # To run manually: uv run pytest tests/unit/application/services/test_agent_rerank_propagation.py
    pass
