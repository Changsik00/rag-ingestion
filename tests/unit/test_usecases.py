from unittest.mock import Mock

from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.scraper import ScraperInterface
from app.schemas.ingest import IngestResponse
from app.use_cases.ingestion import IngestionService


def test_create_job():
    # Arrange
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_job_repo = Mock()
    service = IngestionService(scraper=mock_scraper, repository=mock_doc_repo, job_repository=mock_job_repo)

    # Act
    job = service.create_job("http://example.com")

    # Assert
    assert job.source_url == "http://example.com"
    assert job.status == JobStatus.PENDING
    mock_job_repo.create_job.assert_called_once_with(job)

def test_process_job_success():
    # Arrange
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_job_repo = Mock()

    # Mock Job Retrieval
    mock_job = IngestionJob(source_url="http://example.com", status=JobStatus.PENDING)
    mock_job_repo.get_job.return_value = mock_job

    expected_response = IngestResponse(url="http://example.com/", markdown="# Example", metadata={})
    mock_scraper.scrape.return_value = expected_response

    service = IngestionService(scraper=mock_scraper, repository=mock_doc_repo, job_repository=mock_job_repo)

    # Act
    service.process_job(mock_job.job_id)

    # Assert
    # 1. Scrape & Save
    mock_scraper.scrape.assert_called_once_with("http://example.com")
    mock_doc_repo.save.assert_called_once()

    # 2. Status Updates (RUNNING -> COMPLETED)
    assert mock_job_repo.update_job.call_count == 2

    # Check last update
    args, _ = mock_job_repo.update_job.call_args_list[-1]
    last_updated_job = args[0]
    assert last_updated_job.status == JobStatus.COMPLETED

def test_process_job_failure():
    # Arrange
    mock_scraper = Mock(spec=ScraperInterface)
    mock_scraper.scrape.side_effect = Exception("Scrape failed")
    mock_doc_repo = Mock()
    mock_job_repo = Mock()

    mock_job = IngestionJob(source_url="http://example.com", status=JobStatus.PENDING)
    mock_job_repo.get_job.return_value = mock_job

    service = IngestionService(scraper=mock_scraper, repository=mock_doc_repo, job_repository=mock_job_repo)

    # Act
    # process_job handles exceptions internally, so it should NOT raise
    service.process_job(mock_job.job_id)

    # Assert
    # Status Updates (RUNNING -> FAILED)
    assert mock_job_repo.update_job.call_count == 2

    # Verify Failure Update
    args, _ = mock_job_repo.update_job.call_args_list[-1]
    failed_job = args[0]
    assert failed_job.status == JobStatus.FAILED
    assert "Scrape failed" in failed_job.error_message
