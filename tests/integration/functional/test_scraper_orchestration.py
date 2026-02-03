from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.services.ingestion import Ingestion
from app.domain.entities.job import JobStatus
from app.infrastructure.scrapers.composite_scraper import CompositeScraper
from app.interfaces.api.v1.dto.ingest import IngestResponse


@pytest.fixture
def mock_repositories():
    return {"repository": MagicMock(), "graph": MagicMock(), "job_repository": MagicMock(), "chunker": MagicMock()}


@pytest.fixture
def composite_scraper():
    return CompositeScraper()


@pytest.mark.asyncio
async def test_orchestration_youtube_routing(mock_repositories, composite_scraper):
    """YouTube URL이 적절한 스크래퍼로 라우팅되는지 검증"""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    with patch.object(composite_scraper.youtube_scraper, "scrape", new_callable=AsyncMock) as mock_yt:
        mock_yt.return_value = IngestResponse(
            url=url, markdown="# YouTube Content", metadata={"title": "Test YT", "video_id": "dQw4w9WgXcQ"}
        )

        # Ingestion 서비스 생성
        ingestion = Ingestion(scraper=composite_scraper, **mock_repositories)

        job = ingestion.create_job(url)
        # Mock repository가 생성된 job을 반환하도록 설정
        mock_repositories["job_repository"].get_job.return_value = job
        await ingestion.process_job(job.job_id)

        # YouTube 스크래퍼가 호출되었는지 확인
        mock_yt.assert_called_once_with(url)
        # Job 상태 확인
        mock_repositories["job_repository"].update_job.assert_called()
        last_job_call = mock_repositories["job_repository"].update_job.call_args_list[-1]
        assert last_job_call[0][0].status == JobStatus.COMPLETED


@pytest.mark.asyncio
async def test_orchestration_tiered_fallback(mock_repositories, composite_scraper):
    """Primary 스크래퍼 실패 시 Playwright로 Fallback되는지 검증"""
    url = "https://example.com/dynamic"

    # Tier 1 (Trafilatura) 실패 유도
    with patch.object(composite_scraper.primary_scraper, "scrape", side_effect=Exception("Connection reset")):
        with patch.object(composite_scraper.playwright_scraper, "scrape", new_callable=AsyncMock) as mock_pw:
            mock_pw.return_value = IngestResponse(
                url=url, markdown="# Dynamic Content", metadata={"title": "Test Playwright"}
            )

            ingestion = Ingestion(scraper=composite_scraper, **mock_repositories)

            job = ingestion.create_job(url)
            # Mock repository가 생성된 job을 반환하도록 설정
            mock_repositories["job_repository"].get_job.return_value = job
            await ingestion.process_job(job.job_id)

            # Playwright가 호출되었는지 확인
            mock_pw.assert_called_once_with(url)


@pytest.mark.asyncio
async def test_orchestration_quality_fallback(mock_repositories, composite_scraper):
    """결과 품질이 낮을 때 Playwright로 Fallback되는지 검증"""
    url = "https://example.com/poor"

    # Tier 1이 성공했으나 품질이 낮음
    poor_result = IngestResponse(url=url, markdown="Just a menu item", metadata={})

    with patch.object(composite_scraper.primary_scraper, "scrape", return_value=poor_result):
        with patch.object(composite_scraper.quality_checker, "is_poor", return_value=True):
            with patch.object(composite_scraper.playwright_scraper, "scrape", new_callable=AsyncMock) as mock_pw:
                mock_pw.return_value = IngestResponse(
                    url=url, markdown="# High Quality Content", metadata={"title": "Test Playwright"}
                )

                ingestion = Ingestion(scraper=composite_scraper, **mock_repositories)

                job = ingestion.create_job(url)
                # Mock repository가 생성된 job을 반환하도록 설정
                mock_repositories["job_repository"].get_job.return_value = job
                await ingestion.process_job(job.job_id)

                # Playwright가 호출되었는지 확인
                mock_pw.assert_called_once_with(url)
