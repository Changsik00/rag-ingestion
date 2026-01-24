"""
Spec 035: Transparent Hybrid Knowledge Strategy (BDD Integration Tests)

이 테스트는 DB 정보와 LLM 지식이 조화롭게 융합되고, 출처가 정확히 표기되는지 검증합니다.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from app.domain.entities.chunk import Chunk
from app.domain.schemas.intent import IntentType, UserIntent
from app.domain.services.rag_service import RAGService
from app.infrastructure.rag.nodes import RAGNodes
from app.infrastructure.rag.graph import RAGGraphBuilder

@pytest.fixture
def mock_dependencies():
    # Repositories must return lists for len() to work in nodes.py
    neo4j_doc = Mock()
    neo4j_doc.search.return_value = []
    
    neo4j_graph = Mock()
    neo4j_graph.get_subgraph.return_value = []
    
    chroma = Mock()
    chroma.search_mmr.return_value = []
    
    llm = Mock()
    llm.generate.return_value = Mock(content="")
    
    return {
        "neo4j_doc": neo4j_doc,
        "neo4j_graph": neo4j_graph,
        "chroma": chroma,
        "rewriter": Mock(),
        "intent_classifier": Mock(),
        "llm": llm
    }

@pytest.fixture
def hybrid_rag_service(mock_dependencies):
    nodes = RAGNodes(
        neo4j_doc_repo=mock_dependencies["neo4j_doc"],
        neo4j_graph_repo=mock_dependencies["neo4j_graph"],
        chroma_repo=mock_dependencies["chroma"],
        query_rewriter=mock_dependencies["rewriter"],
        intent_classifier=mock_dependencies["intent_classifier"],
        llm=mock_dependencies["llm"]
    )
    builder = RAGGraphBuilder(nodes)
    graph = builder.build()
    return RAGService(graph)

@pytest.mark.asyncio
async def test_scenario_1_full_rag_answer(hybrid_rag_service, mock_dependencies):
    """
    Scenario 1: Full RAG Base Answer
    - Given: DB에 충분한 정보가 있고
    - When: 답변을 요청하면
    - Then: 모든 정보에 Citation [1]이 붙어야 함
    """
    # Given
    query = "삼성전자의 주력 모델은?"
    mock_dependencies["intent_classifier"].classify.return_value = UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="")
    mock_dependencies["rewriter"].rewrite.return_value = query
    
    chunk = Chunk(id="c1", content="삼성전자의 주력 모델은 갤럭시 S24입니다.", parent_id="d1", index=0, 
                  metadata={"source": "samsung.com", "title": "S24 Specs", "url": "https://samsung.com/s24"})
    mock_dependencies["chroma"].search_mmr.return_value = [chunk]
    mock_dependencies["neo4j_doc"].search.return_value = []
    
    mock_dependencies["llm"].generate.return_value = Mock(content="삼성전자의 주력 모델은 갤럭시 S24입니다[1].")
    
    # When
    result = await hybrid_rag_service.retrieve_and_generate(query, [])
    
    # Then
    assert "[1]" in result.answer
    assert len(result.citations) == 1
    assert result.citations[0]["index"] == 1
    assert result.citations[0]["source"] == "samsung.com"

@pytest.mark.asyncio
async def test_scenario_2_hybrid_mixed_answer(hybrid_rag_service, mock_dependencies):
    """
    Scenario 2: Hybrid Mixed Answer (Sparse but Powerful)
    - Given: 질문 중 일부는 DB에 있고, 일부는 없을 때
    - When: 답변을 요청하면
    - Then: DB 기반 정보에는 [1]이 붙고, LLM 지식에는 번호가 없어야 함
    """
    # Given
    query = "애플과 삼성의 대표 모델 비교"
    mock_dependencies["intent_classifier"].classify.return_value = UserIntent(intent=IntentType.COMPARE, targets=["Apple", "Samsung"], reasoning="")
    
    # 삼성 정보는 DB에 있음
    chunk = Chunk(id="s1", content="삼성은 갤럭시 S24가 대표 모델입니다.", parent_id="d-s", index=0, 
                  metadata={"source": "samsung.com", "title": "Samsung Mobile"})
    mock_dependencies["chroma"].search_mmr.return_value = [chunk]
    mock_dependencies["neo4j_doc"].search.return_value = []
    
    # 애플 정보는 DB에 없음 (LLM이 지식으로 채움)
    # LLM 응답: 삼성은 갤럭시[1]이고, 애플은 아이폰15(번호 없음)입니다.
    mock_dependencies["llm"].generate.return_value = Mock(content="삼성의 대표 모델은 갤럭시 S24입니다[1]. 한편 애플의 최신 모델은 아이폰 15 시리즈로 알려져 있습니다.")
    
    # When
    result = await hybrid_rag_service.retrieve_and_generate(query, [])
    
    # Then
    assert "[1]" in result.answer
    assert "아이폰" in result.answer
    assert len(result.citations) == 1 # 아이폰은 Citation이 없어야 함
    assert result.citations[0]["index"] == 1

@pytest.mark.asyncio
async def test_scenario_3_global_fallback_answer(hybrid_rag_service, mock_dependencies):
    """
    Scenario 3: Global Knowledge Fallback
    - Given: DB에 정보가 전혀 없을 때
    - When: 답변을 요청하면
    - Then: 안내 문구와 함께 LLM 지식으로만 답하고 Citation은 없어야 함
    """
    # Given
    query = "현재 화성의 날씨는?"
    mock_dependencies["chroma"].search_mmr.return_value = []
    mock_dependencies["neo4j_doc"].search.return_value = []
    
    mock_dependencies["llm"].generate.return_value = Mock(content="지식 베이스에 관련 정보가 없어 일반 지식을 바탕으로 답해드립니다. 화성의 날씨는 매우 춥습니다.")
    
    # When
    result = await hybrid_rag_service.retrieve_and_generate(query, [])
    
    # Then
    assert "지식 베이스" in result.answer
    assert len(result.citations) == 0
    assert "[" not in result.answer
