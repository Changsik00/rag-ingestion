import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.saga.ingestion_handlers import IngestionSagaHandlers
from app.core.events import bus
from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.events.ingestion_events import IngestionFailed


@pytest.mark.asyncio
async def test_saga_rollback_on_failure():
    # 1. Setup Mocks
    mock_job_repo = MagicMock()
    mock_doc_repo = AsyncMock()  # Must be AsyncMock for 'delete'
    mock_graph_repo = MagicMock()
    mock_scraper = AsyncMock()
    mock_extractor = AsyncMock()
    mock_chunker = MagicMock()

    # Define a job with some docs to delete on rollback
    job_id = "test-job-id"
    job = IngestionJob(job_id=job_id, source_url="http://fail.com", status=JobStatus.PENDING, docs_ids=["doc1", "doc2"])
    mock_job_repo.get_job.return_value = job

    # 2. Instantiate Saga Handlers
    saga = IngestionSagaHandlers(
        job_repository=mock_job_repo,
        document_repository=mock_doc_repo,
        graph_repository=mock_graph_repo,
        scraper=mock_scraper,
        extractor=mock_extractor,
        chunker=mock_chunker,
    )
    saga.register_all()

    # 3. Simulate Failure Event (e.g., Indexing Failed)
    fail_event = IngestionFailed(job_id=job_id, stage="Indexing", error_message="Connection lost")

    await bus.publish("IngestionFailed", fail_event)
    await asyncio.sleep(0.1)  # Wait for processing

    # 4. Verify Rollback
    # Should update job status
    assert job.status == JobStatus.FAILED
    assert "Connection lost" in job.error_message
    mock_job_repo.update_job.assert_called()

    # Should delete the pre-registered documents
    assert mock_doc_repo.delete.call_count == 2
    mock_doc_repo.delete.assert_any_call("doc1")
    mock_doc_repo.delete.assert_any_call("doc2")


@pytest.mark.asyncio
async def test_saga_success_path():
    # Simplified end-to-end success test if needed
    pass
