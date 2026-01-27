import pytest
from unittest.mock import AsyncMock, MagicMock
from app.infrastructure.rag.nodes import RAGNodes
from app.domain.schemas.intent import UserIntent, IntentType
from app.domain.rag.state import RAGGraphState

@pytest.fixture
def rag_nodes():
    return RAGNodes(
        neo4j_doc_repo=MagicMock(),
        neo4j_graph_repo=MagicMock(),
        chroma_repo=MagicMock(),
        query_rewriter=MagicMock(),
        intent_classifier=MagicMock(),
        llm=MagicMock()
    )

@pytest.mark.asyncio
async def test_retrieve_hybrid_calls_find_shortest_path_when_entities_present(rag_nodes):
    # Given
    entities = ["Elon Musk", "Twitter"]
    user_intent = UserIntent(
        intent=IntentType.GENERAL_QUERY,
        targets=[],
        entities=entities,
        reasoning="Test"
    )
    
    state = RAGGraphState(
        query="Elon and Twitter?",
        history=[],
        user_intent=user_intent,
        rewritten_query="Elon and Twitter relation?",
        vector_chunks=[],
        keyword_chunks=[],
        graph_data=[],
        reasoning_log=[]
    )
    
    # Mock repositories
    rag_nodes.neo4j_graph_repo.find_shortest_path.return_value = [{"source": "A", "rel": "B", "target": "C"}]
    rag_nodes.neo4j_doc_repo.search.return_value = []
    rag_nodes.chroma_repo.search_mmr.return_value = []
    
    # When
    new_state = await rag_nodes.retrieve_hybrid(state)
    
    # Then
    rag_nodes.neo4j_graph_repo.find_shortest_path.assert_called_once_with(entities)
    assert len(new_state["graph_data"]) == 1

@pytest.mark.asyncio
async def test_retrieve_hybrid_calls_get_subgraph_when_no_entities(rag_nodes):
    # Given
    user_intent = UserIntent(
        intent=IntentType.GENERAL_QUERY,
        targets=[],
        entities=[], # Empty entities
        reasoning="Test"
    )
    
    state = RAGGraphState(
        query="General question?",
        history=[],
        user_intent=user_intent,
        rewritten_query="Rewritten General question?",
        vector_chunks=[],
        keyword_chunks=[],
        graph_data=[],
        reasoning_log=[]
    )
    
    # Mock repositories
    rag_nodes.neo4j_graph_repo.get_subgraph.return_value = [{"source": "X", "rel": "Y", "target": "Z"}]
    rag_nodes.neo4j_doc_repo.search.return_value = []
    rag_nodes.chroma_repo.search_mmr.return_value = []
    
    # When
    new_state = await rag_nodes.retrieve_hybrid(state)
    
    # Then
    rag_nodes.neo4j_graph_repo.get_subgraph.assert_called_once_with(["Rewritten General question?"])
    assert len(new_state["graph_data"]) == 1
