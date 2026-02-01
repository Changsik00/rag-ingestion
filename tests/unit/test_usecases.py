"""
Unit Tests for Ingestion

Ingestion의 주요 기능(Job 생성, Job 처리)을 검증합니다.
Mock을 사용하여 의존성을 격리하고 비즈니스 로직만 테스트합니다.
"""

from unittest.mock import Mock

import pytest

from app.application.interfaces.scraper import ScraperInterface
from app.application.services.ingestion import Ingestion
from app.domain.entities.job import IngestionJob, JobStatus
from app.interfaces.api.dto.ingest import IngestResponse


def test_create_job():
    # Given: Ingestion와 mocked dependencies
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_graph_repo = Mock()
    mock_job_repo = Mock()
    mock_chunker = Mock()
    service = Ingestion(
        scraper=mock_scraper,
        repository=mock_doc_repo,
        graph=mock_graph_repo,
        job_repository=mock_job_repo,
        chunker=mock_chunker,
        extractor=None,
    )

    # When: Job 생성 요청
    job = service.create_job("http://example.com")

    # Then: Job이 PENDING 상태로 생성됨
    assert job.source_url == "http://example.com"
    assert job.status == JobStatus.PENDING
    mock_job_repo.create_job.assert_called_once_with(job)


@pytest.mark.asyncio
async def test_process_job_success():
    # Given: Ingestion와 mocked dependencies
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_graph_repo = Mock()
    mock_job_repo = Mock()
    mock_extractor = Mock()

    # Mock Job Retrieval
    mock_job = IngestionJob(source_url="http://example.com", status=JobStatus.PENDING)
    mock_job_repo.get_job.return_value = mock_job

    expected_response = IngestResponse(
        url="http://example.com/", markdown="# Example", metadata={"source_id": "example"}
    )
    mock_scraper.scrape.return_value = expected_response

    # Mock extractor to return None (no semantic data)
    import asyncio

    future = asyncio.Future()
    future.set_result(None)
    mock_extractor.extract.return_value = future

    mock_chunker = Mock()
    service = Ingestion(
        scraper=mock_scraper,
        repository=mock_doc_repo,
        graph=mock_graph_repo,
        job_repository=mock_job_repo,
        chunker=mock_chunker,
        extractor=mock_extractor,
    )

    # When: Job 처리
    await service.process_job(mock_job.job_id)

    # Then: 스크래핑 및 저장 성공, Job 상태가 COMPLETED로 변경
    mock_scraper.scrape.assert_called_once_with("http://example.com")
    mock_doc_repo.save_with_chunks.assert_called_once()
    assert mock_job_repo.update_job.call_count == 2

    # Check last update
    args, _ = mock_job_repo.update_job.call_args_list[-1]
    last_updated_job = args[0]
    assert last_updated_job.status == JobStatus.COMPLETED


@pytest.mark.asyncio
async def test_process_job_failure():
    # Given: 스크래핑 실패를 발생시키는 mock scraper
    mock_scraper = Mock(spec=ScraperInterface)
    mock_scraper.scrape.side_effect = Exception("Scrape failed")
    mock_doc_repo = Mock()
    mock_graph_repo = Mock()
    mock_job_repo = Mock()

    mock_job = IngestionJob(source_url="http://example.com", status=JobStatus.PENDING)
    mock_job_repo.get_job.return_value = mock_job

    mock_chunker = Mock()
    service = Ingestion(
        scraper=mock_scraper,
        repository=mock_doc_repo,
        graph=mock_graph_repo,
        job_repository=mock_job_repo,
        chunker=mock_chunker,
        extractor=None,
    )

    # When: Job 처리 (예외가 내부에서 처리됨)
    await service.process_job(mock_job.job_id)

    # Then: Job 상태가 FAILED로 변경됨
    assert mock_job_repo.update_job.call_count == 2

    # Verify Failure Update
    args, _ = mock_job_repo.update_job.call_args_list[-1]
    failed_job = args[0]
    assert failed_job.status == JobStatus.FAILED
    assert "Scrape failed" in failed_job.error_message
