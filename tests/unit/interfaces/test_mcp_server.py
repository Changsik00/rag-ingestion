from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.interfaces.mcp.server import ingest_url, search_knowledge_base


@pytest.mark.asyncio
async def test_ingest_url_tool():
    # Mocking the service behavior
    mock_ingestion_service = MagicMock()  # Not AsyncMock because create_job is sync

    mock_job = MagicMock()
    mock_job.job_id = "job-123"
    mock_job.status = "COMPLETED"
    mock_job.status = "COMPLETED"
    # mock_job.metadata does not exist on IngestionJob

    mock_ingestion_service.create_job.return_value = mock_job
    mock_ingestion_service.job_repository.get_job.return_value = mock_job

    with patch("app.interfaces.mcp.server.provide_ingestion_service") as mock_get_service:
        mock_get_service.return_value = mock_ingestion_service

        result = await ingest_url("http://test.com")

        mock_ingestion_service.create_job.assert_called_once_with("http://test.com")
        mock_ingestion_service.process_job.assert_called_once_with("job-123")
        assert "Successfully ingested" in result


@pytest.mark.asyncio
async def test_search_knowledge_base_tool():
    """Test search_knowledge_base tool calling RAGService"""
    # Initialize Mock
    mock_rag_service = AsyncMock()

    # Mock return value of RAGService
    mock_result = MagicMock()
    mock_result.answer = "Test Answer"
    mock_result.full_context = "Context"

    mock_rag_service.retrieve_and_generate.return_value = mock_result

    with patch("app.interfaces.mcp.server.provide_rag_service") as mock_get_service:
        mock_get_service.return_value = mock_rag_service

        result = await search_knowledge_base("test query")

        mock_rag_service.retrieve_and_generate.assert_called_once_with("test query", [])
        assert "Answer: Test Answer" in result
