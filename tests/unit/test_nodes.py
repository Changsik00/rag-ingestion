import pytest
from src.domain.state import GraphState
from src.application.nodes.mock_nodes import fetch_source_node, extract_content_node

def test_fetch_source_node():
    """fetch_source_node가 URL을 받아 Source 객체를 생성하는지 검증"""
    # Given
    initial_state: GraphState = {
        "urls": ["https://test.com"],
        "sources": [],
        "errors": [],
        "status": "init"
    }

    # When
    new_state = fetch_source_node(initial_state)

    # Then
    assert len(new_state["sources"]) == 1
    assert str(new_state["sources"][0].url) == "https://test.com/"
    assert "dummy content" in new_state["sources"][0].raw_content
    assert new_state["status"] == "fetched"

def test_extract_content_node():
    """extract_content_node가 Source에서 Chunk를 생성하는지 검증"""
    # Given (Fetch 단계가 완료된 상태 가정)
    from src.domain.models.source import Source
    source = Source(url="https://test.com", raw_content="Dummy Content")
    
    pre_state: GraphState = {
        "urls": [],
        "sources": [source],
        "errors": [],
        "status": "fetched"
    }

    # When
    new_state = extract_content_node(pre_state)

    # Then
    assert len(new_state["sources"][0].chunks) > 0
    assert new_state["sources"][0].chunks[0].content == "Chunk 1 from Dummy Content"
    assert new_state["status"] == "extracted"
