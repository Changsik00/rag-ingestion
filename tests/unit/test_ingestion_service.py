from unittest.mock import Mock

import pytest

from app.core.exceptions import InfrastructureException, ScrapingError
from app.domain.entities.job import IngestionJob, JobStatus
from app.use_cases.ingestion import IngestionService


@pytest.fixture
def service_deps():
    return {
        "scraper": Mock(),
        "repository": Mock(),
        "graph": Mock(),
        "job_repository": Mock(),
        "extractor": Mock(),
        "chunker": Mock(),
    }


def test_process_job_handles_scraping_error(service_deps):
    """
    Given: Scraper raises ScrapingError
    When: process_job is called
    Then: Job status becomes FAILED and error is logged (not crashed)
    """
    # Given
    job_id = "job-123"
    job = IngestionJob(id=job_id, source_url="http://fail.com", status=JobStatus.PENDING)

    service_deps["job_repository"].get_job.return_value = job
    service_deps["scraper"].scrape.side_effect = ScrapingError("404 Not Found")

    service = IngestionService(**service_deps)

    # When
    service.process_job(job_id)

    # Then
    service_deps["job_repository"].update_job.assert_called()
    updated_job = service_deps["job_repository"].update_job.call_args[0][0]
    assert updated_job.status == JobStatus.FAILED
    assert "404 Not Found" in updated_job.error_message


def test_process_job_handles_infrastructure_exception(service_deps):
    """
    Given: Repository raises InfrastructureException
    When: process_job is called
    Then: Job status becomes FAILED
    """
    # Given
    job_id = "job-456"
    job = IngestionJob(id=job_id, source_url="http://success.com", status=JobStatus.PENDING)

    service_deps["job_repository"].get_job.return_value = job

    # Scrape succeeds
    mock_result = Mock()
    mock_result.markdown = "content"
    mock_result.url = "http://success.com"
    mock_result.metadata = {}
    service_deps["scraper"].scrape.return_value = mock_result

    # Repo fails
    service_deps["repository"].save_with_chunks.side_effect = InfrastructureException("DB Connection Failed")
    service_deps["extractor"].extract.return_value = None  # Disable extraction logic for this test

    service = IngestionService(**service_deps)

    # Chunking mock setup to return list (iterable) just in case
    service_deps["chunker"].chunk_document.return_value = []

    # When
    service.process_job(job_id)

    # Then
    service_deps["job_repository"].update_job.assert_called()
    updated_job = service_deps["job_repository"].update_job.call_args[0][0]
    assert updated_job.status == JobStatus.FAILED
    assert "DB Connection Failed" in updated_job.error_message


def test_process_job_chunks_document(service_deps):
    """
    Given: ChunkerService splits document into chunks
    When: process_job is called
    Then: repository.save_with_chunks is called with document and chunks
    """
    # Given
    job_id = "job-chunks"
    job = IngestionJob(id=job_id, source_url="http://chunk.com", status=JobStatus.PENDING)
    service_deps["job_repository"].get_job.return_value = job
    service_deps["extractor"].extract.return_value = None  # Disable extraction

    # Scrape succeeds
    mock_result = Mock()
    mock_result.markdown = "Full content that will be chunked"
    mock_result.url = "http://chunk.com"
    mock_result.metadata = {}
    service_deps["scraper"].scrape.return_value = mock_result

    # Chunker Mock
    mock_chunker = Mock()
    chunk1 = Mock(content="Content 1")
    chunk2 = Mock(content="Content 2")
    chunks = [chunk1, chunk2]
    mock_chunker.chunk_document.return_value = chunks
    service_deps["chunker"] = mock_chunker  # Inject chunker

    service = IngestionService(**service_deps)

    # When
    service.process_job(job_id)

    # Then
    # 1. Chunker called
    mock_chunker.chunk_document.assert_called_once()

    # 2. Repository save_with_chunks called instead of save
    service_deps["repository"].save_with_chunks.assert_called_once()
    args = service_deps["repository"].save_with_chunks.call_args[0]
    doc = args[0]
    saved_chunks = args[1]

    assert doc.content == "Full content that will be chunked"
    assert saved_chunks == chunks

    # check job completion
    final_job = service_deps["job_repository"].update_job.call_args[0][0]
    assert final_job.status == JobStatus.COMPLETED
