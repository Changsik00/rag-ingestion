from unittest.mock import Mock

from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.scraper import ScraperInterface
from app.schemas.ingest import IngestResponse
from app.use_cases.ingestion import IngestionService


def test_create_job():
    # Given: IngestionService와 mocked dependencies
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_graph_repo = Mock()
    mock_job_repo = Mock()
    service = IngestionService(
        scraper=mock_scraper,
        repository=mock_doc_repo,
        graph=mock_graph_repo,
        job_repository=mock_job_repo,
        extractor=None
    )

    # When: Job 생성 요청
    job = service.create_job("http://example.com")

    # Then: Job이 PENDING 상태로 생성됨
    assert job.source_url == "http://example.com"
    assert job.status == JobStatus.PENDING
    mock_job_repo.create_job.assert_called_once_with(job)

def test_process_job_success():
    # Given: IngestionService와 mocked dependencies
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_graph_repo = Mock()
    mock_job_repo = Mock()
    mock_extractor = Mock()

    # Mock Job Retrieval
    mock_job = IngestionJob(source_url="http://example.com", status=JobStatus.PENDING)
    mock_job_repo.get_job.return_value = mock_job

    expected_response = IngestResponse(url="http://example.com/", markdown="# Example", metadata={})
    mock_scraper.scrape.return_value = expected_response
    
    # Mock extractor to return None (no semantic data)
    mock_extractor.extract.return_value = None

    service = IngestionService(
        scraper=mock_scraper,
        repository=mock_doc_repo,
        graph=mock_graph_repo,
        job_repository=mock_job_repo,
        extractor=mock_extractor
    )

    # When: Job 처리
    service.process_job(mock_job.job_id)

    # Then: 스크래핑 및 저장 성공, Job 상태가 COMPLETED로 변경
    mock_scraper.scrape.assert_called_once_with("http://example.com")
    mock_doc_repo.save.assert_called_once()
    assert mock_job_repo.update_job.call_count == 2

    # Check last update
    args, _ = mock_job_repo.update_job.call_args_list[-1]
    last_updated_job = args[0]
    assert last_updated_job.status == JobStatus.COMPLETED

def test_process_job_failure():
    # Given: 스크래핑 실패를 발생시키는 mock scraper
    mock_scraper = Mock(spec=ScraperInterface)
    mock_scraper.scrape.side_effect = Exception("Scrape failed")
    mock_doc_repo = Mock()
    mock_graph_repo = Mock()
    mock_job_repo = Mock()

    mock_job = IngestionJob(source_url="http://example.com", status=JobStatus.PENDING)
    mock_job_repo.get_job.return_value = mock_job

    service = IngestionService(
        scraper=mock_scraper,
        repository=mock_doc_repo,
        graph=mock_graph_repo,
        job_repository=mock_job_repo,
        extractor=None
    )

    # When: Job 처리 (예외가 내부에서 처리됨)
    service.process_job(mock_job.job_id)

    # Then: Job 상태가 FAILED로 변경됨
    assert mock_job_repo.update_job.call_count == 2

    # Verify Failure Update
    args, _ = mock_job_repo.update_job.call_args_list[-1]
    failed_job = args[0]
    assert failed_job.status == JobStatus.FAILED
    assert "Scrape failed" in failed_job.error_message
