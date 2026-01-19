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
        "extractor": Mock()
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
    service_deps["repository"].save.side_effect = InfrastructureException("DB Connection Failed")

    service = IngestionService(**service_deps)

    # When
    service.process_job(job_id)

    # Then
    service_deps["job_repository"].update_job.assert_called()
    updated_job = service_deps["job_repository"].update_job.call_args[0][0]
    assert updated_job.status == JobStatus.FAILED
    assert "DB Connection Failed" in updated_job.error_message
