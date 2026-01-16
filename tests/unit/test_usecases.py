from unittest.mock import Mock, ANY
import pytest
from app.use_cases.ingestion import IngestionService
from app.domain.interfaces.scraper import ScraperInterface
from app.schemas.ingest import IngestResponse
from app.domain.entities.job import JobStatus

def test_ingest_web_page_success():
    # Arrange
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_job_repo = Mock()
    
    expected_response = IngestResponse(url="http://example.com/", markdown="# Example", metadata={})
    mock_scraper.scrape.return_value = expected_response
    
    service = IngestionService(scraper=mock_scraper, repository=mock_doc_repo, job_repository=mock_job_repo)
    
    # Act
    result = service.ingest("http://example.com")
    
    # Assert
    assert result == expected_response
    mock_scraper.scrape.assert_called_once_with("http://example.com")
    mock_doc_repo.save.assert_called_once()
    
    # Job verification
    # 1. Created (PENDING)
    mock_job_repo.create_job.assert_called_once()
    created_job = mock_job_repo.create_job.call_args[0][0]
    assert created_job.source_url == "http://example.com"
    # Note: created_job is mutable and updated in place, so it will be COMPLETED by now
    
    # 2. Updated (COMPLETED)
    mock_job_repo.update_job.assert_called_once()
    updated_job = mock_job_repo.update_job.call_args[0][0]
    assert updated_job.job_id == created_job.job_id
    assert updated_job.status == JobStatus.COMPLETED

def test_ingest_web_page_failure():
    # Arrange
    mock_scraper = Mock(spec=ScraperInterface)
    mock_scraper.scrape.side_effect = Exception("Scrape failed")
    mock_doc_repo = Mock()
    mock_job_repo = Mock()
    
    service = IngestionService(scraper=mock_scraper, repository=mock_doc_repo, job_repository=mock_job_repo)
    
    # Act
    with pytest.raises(Exception):
        service.ingest("http://example.com")
        
    # Assert
    mock_job_repo.create_job.assert_called_once()
    
    # Verify Failure Update
    mock_job_repo.update_job.assert_called_once()
    updated_job = mock_job_repo.update_job.call_args[0][0]
    assert updated_job.status == JobStatus.FAILED
    assert "Scrape failed" in updated_job.error_message
