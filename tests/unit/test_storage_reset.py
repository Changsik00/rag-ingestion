from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.infrastructure.ai.orchestrators.ingestion_orchestrator import IngestionOrchestrator
from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository


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
    storage = Neo4jDocumentRepository(mock_neo4j_driver)

    # When
    storage.reset_database()

    # Then
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    # Expect DETACH DELETE query
    session.run.assert_called_with("MATCH (n) DETACH DELETE n")


@patch("app.infrastructure.repositories.chroma.get_settings")
@patch("app.infrastructure.repositories.chroma.GoogleGenerativeAIEmbeddings")
@patch("app.infrastructure.repositories.chroma.chromadb.HttpClient")
def test_chroma_reset_collection(mock_http_client, mock_embeddings, mock_settings):
    # Given
    mock_settings.return_value.GEMINI_API_KEY = "dummy"
    mock_settings.return_value.CHROMA_HOST = "localhost"
    mock_settings.return_value.CHROMA_PORT = 8000

    client_instance = mock_http_client.return_value
    collection_mock = MagicMock()
    client_instance.get_or_create_collection.return_value = collection_mock

    storage = ChromaVectorRepository()

    # When
    storage.reset_collection()

    # Then
    # We expect the client to delete and recreate the collection, OR the client to call reset() if enabled
    # But usually we reset the specific collection.
    # Common pattern: client.delete_collection("documents") -> get_or_create_collection("documents")
    # Let's assume implementation will do delete then create.
    client_instance.delete_collection.assert_called_with(name="documents")
    client_instance.get_or_create_collection.assert_called()


@pytest.mark.asyncio
async def test_langgraph_adapter_reset_checkpoints():
    # Given
    mock_llm = MagicMock()
    mock_checkpointer = AsyncMock(spec=AsyncSqliteSaver)
    # Mock the connection attribute
    # aiosqlite conn.execute returns an IDLE cursor which is an async context manager.
    # It is NOT awaited directly. So execute should be a MagicMock, not AsyncMock.
    mock_conn = MagicMock()
    mock_checkpointer.conn = mock_conn

    # Setup execute to return an async context manager
    mock_cursor_ctx = AsyncMock()
    mock_cursor_ctx.__aenter__.return_value = MagicMock()
    mock_cursor_ctx.__aexit__.return_value = None

    mock_conn.execute.return_value = mock_cursor_ctx

    # Commit is an async method in aiosqlite
    mock_conn.commit = AsyncMock()

    adapter = IngestionOrchestrator(llm=mock_llm, checkpointer=mock_checkpointer)

    # When
    await adapter.reset_checkpoints()

    # Then
    # We expect raw SQL execution on the connection
    # Note: AsyncSqliteSaver uses `async with self.conn.executemany(...)` or similar.
    # We verify that standard DELETE queries were executed.
    assert mock_conn.execute.call_count >= 1
    call_args_list = mock_conn.execute.call_args_list

    # Check if critical tables are cleared
    executed_sqls = [args[0] for args, _ in call_args_list]
    assert any("DELETE FROM checkpoints" in sql for sql in executed_sqls)
    assert any("DELETE FROM checkpoint_blobs" in sql for sql in executed_sqls)
    assert any("DELETE FROM checkpoint_writes" in sql for sql in executed_sqls)

    # Ensure commit was called
    mock_conn.commit.assert_called()
