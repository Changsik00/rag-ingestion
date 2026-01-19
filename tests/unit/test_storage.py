"""
Unit Tests for CompositeStorage

CompositeStorage의 Document 저장 및 조회 기능을 검증합니다.
Neo4j와 ChromaDB 저장소를 조합하여 사용하는 패턴을 테스트합니다.
"""

from unittest.mock import Mock
from uuid import uuid4

from app.domain.entities.document import AtomicDocument
from app.infrastructure.storage.composite import CompositeStorage


def test_composite_storage_save():
    # Given: CompositeStorage와 Document
    neo4j_mock = Mock()
    chroma_mock = Mock()
    storage = CompositeStorage(neo4j=neo4j_mock, chroma=chroma_mock)

    doc = AtomicDocument(content="Test", source_url="http://test.com")

    # When: Document 저장
    storage.save(doc)

    # Then: 두 저장소 모두에 저장됨
    neo4j_mock.save.assert_called_once_with(doc)
    chroma_mock.save.assert_called_once_with(doc)


def test_composite_storage_get():
    # Given: CompositeStorage와 Mock data
    neo4j_mock = Mock()
    chroma_mock = Mock()
    doc_id = uuid4()
    expected_doc = AtomicDocument(id=doc_id, content="Test", source_url="http://test.com")

    # Neo4j is the source of truth for metadata/structure
    neo4j_mock.get.return_value = expected_doc

    storage = CompositeStorage(neo4j=neo4j_mock, chroma=chroma_mock)

    # When: Document 조회
    result = storage.get(doc_id)

    # Then: Neo4j에서 Document 반환
    assert result == expected_doc
    neo4j_mock.get.assert_called_once_with(doc_id)
