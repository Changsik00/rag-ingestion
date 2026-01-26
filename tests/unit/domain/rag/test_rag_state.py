"""
RAGGraphState 단위 테스트.
"""

from app.domain.rag.state import RAGGraphState


def test_rag_graph_state_has_citations_field():
    """
    RAGGraphState에 citations 필드가 있는지 확인합니다.
    """
    # Given: citations 필드가 포함된 상태 딕셔너리
    state: RAGGraphState = {
        "query": "test",
        "history": [],
        "manual_filters": None,
        "user_intent": None,
        "rewritten_query": None,
        "auto_filters": None,
        "final_filters": None,
        "vector_chunks": [],
        "keyword_chunks": [],
        "graph_data": [],
        "fallback_triggered": False,
        "reasoning_log": [],
        "full_context": "",
        "final_answer": "",
        "citations": [
            {"index": 1, "source": "test_source", "url": "http://test.com", "title": "Test Title"}
        ]
    }

    # Then: citations 필드에 접근 가능해야 함
    assert len(state["citations"]) == 1
    assert state["citations"][0]["index"] == 1
    assert state["citations"][0]["title"] == "Test Title"
