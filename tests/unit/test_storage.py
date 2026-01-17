from unittest.mock import Mock
from uuid import uuid4

from app.domain.entities.document import AtomicDocument
from app.infrastructure.storage.composite import CompositeStorage


def test_composite_storage_save():
    # Arrange
    neo4j_mock = Mock()
    chroma_mock = Mock()
    storage = CompositeStorage(neo4j=neo4j_mock, chroma=chroma_mock)

    doc = AtomicDocument(content="Test", source_url="http://test.com")

    # Act
    storage.save(doc)

    # Assert
    neo4j_mock.save.assert_called_once_with(doc)
    chroma_mock.save.assert_called_once_with(doc)

def test_composite_storage_get():
    # Arrange
    neo4j_mock = Mock()
    chroma_mock = Mock()
    doc_id = uuid4()
    expected_doc = AtomicDocument(id=doc_id, content="Test", source_url="http://test.com")

    # Neo4j is the source of truth for metadata/structure
    neo4j_mock.get.return_value = expected_doc

    storage = CompositeStorage(neo4j=neo4j_mock, chroma=chroma_mock)

    # Act
    result = storage.get(doc_id)

    # Assert
    assert result == expected_doc
    neo4j_mock.get.assert_called_once_with(doc_id)
