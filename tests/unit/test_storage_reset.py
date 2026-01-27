import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.infrastructure.storage.chroma import ChromaStorage

@pytest.fixture
def mock_neo4j_driver():
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__.return_value = session
    return driver

@pytest.fixture
def mock_chroma_client():
    client = MagicMock()
    collection = MagicMock()
    client.get_or_create_collection.return_value = collection
    return client

def test_neo4j_reset_database(mock_neo4j_driver):
    # Given
    storage = Neo4jStorage(mock_neo4j_driver)
    
    # When
    storage.reset_database()
    
    # Then
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    # Expect DETACH DELETE query
    session.run.assert_called_with("MATCH (n) DETACH DELETE n")

@patch("app.infrastructure.storage.chroma.get_settings")
@patch("app.infrastructure.storage.chroma.GoogleGenerativeAIEmbeddings")
@patch("app.infrastructure.storage.chroma.chromadb.HttpClient")
def test_chroma_reset_collection(mock_http_client, mock_embeddings, mock_settings):
    # Given
    mock_settings.return_value.GEMINI_API_KEY = "dummy"
    mock_settings.return_value.CHROMA_HOST = "localhost"
    mock_settings.return_value.CHROMA_PORT = 8000
    
    client_instance = mock_http_client.return_value
    collection_mock = MagicMock()
    client_instance.get_or_create_collection.return_value = collection_mock
    
    storage = ChromaStorage()
    
    # When
    storage.reset_collection()
    
    # Then
    # We expect the client to delete and recreate the collection, OR the client to call reset() if enabled
    # But usually we reset the specific collection.
    # Common pattern: client.delete_collection("documents") -> get_or_create_collection("documents")
    # Let's assume implementation will do delete then create.
    client_instance.delete_collection.assert_called_with(name="documents")
    client_instance.get_or_create_collection.assert_called()
