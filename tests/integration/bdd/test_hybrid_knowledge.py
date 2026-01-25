"""
Spec 035: Transparent Hybrid Knowledge Strategy (BDD Integration Tests)

이 테스트는 DB 정보와 LLM 지식이 조화롭게 융합되고, 출처가 정확히 표기되는지 검증합니다.
기존의 순환 참조식 MOCK을 제거하고, 지저분한 위키피디아 데이터를 시뮬레이션하여 검증합니다.
"""

from unittest.mock import Mock, AsyncMock
from uuid import uuid4

import pytest

from app.domain.entities.chunk import Chunk
from app.domain.schemas.intent import IntentType, UserIntent
from app.domain.services.rag_service import RAGService
from app.infrastructure.rag.graph import RAGGraphBuilder
from app.infrastructure.rag.nodes import RAGNodes


@pytest.fixture
def mock_dependencies():
    neo4j_doc = Mock()
    neo4j_graph = Mock()
    chroma = Mock()
    llm = Mock()

    # Default returns to prevent errors
    neo4j_doc.search.return_value = []
    neo4j_graph.get_subgraph.return_value = []
    chroma.search_mmr.return_value = []

    return {
        "neo4j_doc": neo4j_doc,
        "neo4j_graph": neo4j_graph,
        "chroma": chroma,
        "rewriter": AsyncMock(),
        "intent_classifier": AsyncMock(),
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
async def test_scenario_realistic_wikipedia_and_multiple_citations(hybrid_rag_service, mock_dependencies):
    """
    Scenario: Realistic Wikipedia Snippets with Multiple Citations
    - Given: 지저분한 위키피디아 청크(표, 링크 포함)가 DB에 2개 있을 때
    - When: 두 정보를 모두 포함하는 질문을 던지면
    - Then: [1][2] 형태의 복수 출처가 생성되고, 메타데이터가 정확히 매핑되어야 함
    """
    # 1. Given: Noisy Wikipedia Chunks
    query = "일론 머스크의 우주 사업 성과는?"

    # Chunk 1: Table and links noise
    content_1 = """| 연도 | 발사체 | 결과 |
| --- | --- | --- |
| 2002 | 팰컨 1 | 실패 |
| 2008 | 팰컨 1 | 성공 |
SpaceX는 일론 머스크가 설립한 우주 탐사 기업입니다."""
    chunk_1 = Chunk(id=str(uuid4()), content=content_1, parent_id=str(uuid4()), index=0,
                    metadata={"source": "wikipedia.org", "title": "SpaceX History", "url": "https://ko.wikipedia.org/wiki/SpaceX"})

    # Chunk 2: Extra noise
    content_2 = """### 테슬라와의 관계
일론 머스크는 테슬라의 CEO이기도 하며, 자신의 개인 제트기를 이용해 이동합니다.[1] Icons8_flat_search.svg/20px-Icons8... 이 부분은 무시하십시오."""
    chunk_2 = Chunk(id=str(uuid4()), content=content_2, parent_id=str(uuid4()), index=1,
                    metadata={"source": "wikipedia.org", "title": "Elon Musk Bio", "url": "https://ko.wikipedia.org/wiki/Elon_Musk"})

    mock_dependencies["intent_classifier"].classify.return_value = UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="Test")
    mock_dependencies["rewriter"].rewrite.return_value = query
    mock_dependencies["chroma"].search_mmr.return_value = [chunk_1, chunk_2]

    # LLM Mock: Should generate citations [1] and [2]
    # We use a side_effect to verify the context actually contains our noisy data
    def llm_side_effect(prompt):
        assert "SpaceX는 일론 머스크가 설립" in prompt
        assert "테슬라의 CEO이기도 하며" in prompt
        return Mock(content="일론 머스크는 SpaceX를 설립하여 2008년 팰컨 1 발사에 성공했습니다[1]. 또한 그는 테슬라의 CEO로서 자신의 개인 제트기를 사용합니다[2].")

    mock_dependencies["llm"].generate.side_effect = llm_side_effect

    # 2. When
    result = await hybrid_rag_service.retrieve_and_generate(query, [])

    # 3. Then
    assert "[1]" in result.answer
    assert "[2]" in result.answer
    assert len(result.citations) == 2

    # Verify Metadata Mapping
    citation_1 = next(c for c in result.citations if c["index"] == 1)
    assert citation_1["title"] == "SpaceX History"
    assert citation_1["url"] == "https://ko.wikipedia.org/wiki/SpaceX"

    citation_2 = next(c for c in result.citations if c["index"] == 2)
    assert citation_2["title"] == "Elon Musk Bio"
    assert "Elon_Musk" in citation_2["url"]

@pytest.mark.asyncio
async def test_scenario_hallucinated_citation_protection(hybrid_rag_service, mock_dependencies):
    """
    Scenario: Protection against Hallucinated Citations
    - Given: DB에 청크가 1개만 있는데
    - When: LLM이 환각을 일으켜 존재하지 않는 인덱스 [99]를 생성했을 때
    - Then: [99]는 무시되고, 실제 존재하는 [1]만 Citation 리스트에 포함되어야 함
    """
    # 1. Given
    query = "테슬라의 모델 라인업은?"
    chunk = Chunk(id=str(uuid4()), content="테슬라는 모델 S, 3, X, Y를 판매합니다.", parent_id=str(uuid4()), index=0,
                  metadata={"source": "tesla.com", "title": "Models"})

    mock_dependencies["intent_classifier"].classify.return_value = UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="Test")
    mock_dependencies["rewriter"].rewrite.return_value = query
    mock_dependencies["chroma"].search_mmr.return_value = [chunk]

    # LLM Answer with hallucinated [99]
    mock_dependencies["llm"].generate.return_value = Mock(
        content="테슬라의 주요 라인업은 S, 3, X, Y입니다[1]. 그리고 곧 모델 2도 출시될 예정입니다[99]."
    )

    # 2. When
    result = await hybrid_rag_service.retrieve_and_generate(query, [])

    # 3. Then
    # Answer text still contains [99] (as generated), but citations metadata list should ONLY have [1]
    assert "[99]" in result.answer
    assert len(result.citations) == 1
    assert result.citations[0]["index"] == 1
    assert all(c["index"] != 99 for c in result.citations)

@pytest.mark.asyncio
async def test_scenario_pure_llm_fallback_no_citation(hybrid_rag_service, mock_dependencies):
    """
    Scenario: Pure LLM Fallback (No DB Context)
    - Given: 검색 결과가 전혀 없을 때
    - When: 질문에 답하면
    - Then: 답변에 어떤 대괄호 [] 패턴도 없어야 하며, citations 리스트는 비어있어야 함
    """
    # 1. Given
    query = "세상에서 가장 맛있는 라면은?"
    mock_dependencies["chroma"].search_mmr.return_value = []
    mock_dependencies["neo4j_doc"].search.return_value = []

    mock_dependencies["intent_classifier"].classify.return_value = UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="Test")
    mock_dependencies["rewriter"].rewrite.return_value = query

    # LLM answer without citations
    mock_dependencies["llm"].generate.return_value = Mock(
        content="라면의 맛은 주관적이지만, 신라면과 진라면이 한국에서 가장 인기가 많습니다."
    )

    # 2. When
    result = await hybrid_rag_service.retrieve_and_generate(query, [])

    # 3. Then
    assert "[" not in result.answer
    assert "]" not in result.answer
    assert len(result.citations) == 0
