from unittest.mock import Mock, patch
from uuid import uuid4
import pytest
from app.core.exceptions import InfrastructureException
from app.domain.entities.document import AtomicDocument
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.composite import CompositeStorage

# ... existing CompositeStorage tests ...

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

# --- New Tests for ChromaStorage Hardening ---

@patch("chromadb.HttpClient")
@patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"})
def test_chroma_storage_save_exception_handling(mock_client_cls):
    """
    Given: ChromaDB client raises an exception during save
    When: save() is called
    Then: It should be wrapped in InfrastructureException
    """
    # Setup
    mock_client = Mock()
    mock_collection = Mock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client_cls.return_value = mock_client
    
    # Simulate ChromaDB failure
    mock_collection.add.side_effect = Exception("Connection Refused")
    
    storage = ChromaStorage()
    doc = AtomicDocument(content="Test", source_url="http://test.com")
    
    # Verify exception wrapping
    with pytest.raises(InfrastructureException) as exc_info:
        storage.save(doc)
    
    assert "Failed to save document to ChromaDB" in str(exc_info.value) or "Connection Refused" in str(exc_info.value)

@patch("chromadb.HttpClient")
@patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"})
def test_chroma_storage_get_null_safety(mock_client_cls):
    """
    Given: ChromaDB returns malformed result (None or empty lists)
    When: get() is called
    Then: It should safely return None without crashing
    """
    mock_client = Mock()
    mock_collection = Mock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client_cls.return_value = mock_client
    
    storage = ChromaStorage()
    doc_id = uuid4()
    
    # Case 1: Result is None
    mock_collection.get.return_value = None
    assert storage.get(doc_id) is None
    
    # Case 2: Result has empty 'documents' list
    mock_collection.get.return_value = {"ids": [], "documents": [], "metadatas": []}
    assert storage.get(doc_id) is None
    
    # Case 3: Result has None in 'documents' (if possible in library)
    mock_collection.get.return_value = {"ids": ["1"], "documents": [], "metadatas": []}
    assert storage.get(doc_id) is None
