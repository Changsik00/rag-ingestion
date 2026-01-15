import pytest
from src.domain.state import GraphState
from src.domain.models.source import Source

def test_graph_state_structure():
    """GraphState가 TypedDict로서 올바른 구조를 가지는지 검증"""
    state: GraphState = {
        "urls": ["https://test.com"],
        "sources": [],
        "errors": [],
        "status": "pending"
    }

    assert state["urls"] == ["https://test.com"]
    assert len(state["sources"]) == 0
    assert state["status"] == "pending"

def test_graph_state_with_sources():
    """Source 객체를 포함한 State 검증"""
    source = Source(url="https://test.com")
    state: GraphState = {
        "urls": [],
        "sources": [source],
        "errors": [],
        "status": "processing"
    }
    
    assert len(state["sources"]) == 1
    assert str(state["sources"][0].url) == "https://test.com/"
