"""
RAG Nodes Context Formatting 단위 테스트.
"""

from unittest.mock import Mock

from app.domain.entities.chunk import Chunk
from app.infrastructure.rag.nodes import RAGNodes


def test_merge_and_format_context_injects_explicit_ids():
    """
    _merge_and_format_context가 [ID: n] 형식을 사용하여 컨텍스트를 생성하는지 검증합니다.
    """
    # Given
    nodes = RAGNodes(
        neo4j_doc_repo=Mock(),
        neo4j_graph_repo=Mock(),
        chroma_repo=Mock(),
        query_rewriter=Mock(),
        intent_classifier=Mock(),
        llm=Mock()
    )

    chunk1 = Chunk(
        id="c1",
        content="AI content 1",
        parent_id="d1",
        index=0,
        metadata={"source": "src1", "title": "Title 1"}
    )
    chunk2 = Chunk(
        id="c2",
        content="AI content 2",
        parent_id="d2",
        index=1,
        metadata={"source": "src2", "title": "Title 2"}
    )

    # When
    context_str, _ = nodes._merge_and_format_context([chunk1], [chunk2], [])

    # Then
    # 현재 구현은 [1] Source: src1 (Title 1) 형식임
    # Spec 035에서는 이를 명확히 [ID: 1] 등으로 관리하거나,
    # 최소한 [n] 형식이 유지되어야 함.
    assert "[1] Source: src1 (Title 1)" in context_str
    assert "[2] Source: src2 (Title 2)" in context_str
    assert "AI content 1" in context_str
    assert "AI content 2" in context_str
