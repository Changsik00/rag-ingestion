"""
[Spec 072] End-to-End Tests for Deduplication Framework

These tests verify the full deduplication flow with real databases.
Run with: docker-compose up -d neo4j chromadb && uv run pytest tests/e2e/test_deduplication_end_to_end.py -v --e2e
"""

import pytest

from app.application.services.ingestion import Ingestion
from app.domain.entities.job import JobStatus
from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.infrastructure.repositories.neo4j_job_repository import Neo4jJobRepository
from app.infrastructure.scrapers.composite_scraper import CompositeScraper
from app.interfaces.api.dependencies import get_neo4j_driver


@pytest.mark.e2e
class TestDeduplicationEndToEnd:
    """End-to-End tests for deduplication with real databases"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup real database connections"""
        # Initialize Neo4j
        driver = get_neo4j_driver()
        self.job_repository = Neo4jJobRepository(driver)

        # Initialize ChromaDB
        self.doc_repository = ChromaVectorRepository()

        # Initialize Scraper
        self.scraper = CompositeScraper()

        # Initialize Graph (mock for now, can be real if needed)
        from unittest.mock import Mock

        self.graph = Mock()

        # Initialize Ingestion Service
        self.ingestion = Ingestion(
            scraper=self.scraper,
            repository=self.doc_repository,
            graph=self.graph,
            job_repository=self.job_repository,
        )

        yield

        # Cleanup: Delete test jobs
        driver.close()

    @pytest.mark.asyncio
    async def test_duplicate_job_is_skipped(self):
        """
        [Spec 072] Test: 동일 URL을 2번 수집하면 2번째는 SKIPPED 상태가 되어야 함
        """
        test_url = "https://example.com/test-dedup"

        # 1. First ingestion: Create and process job
        job1 = self.ingestion.create_job(url=test_url)
        await self.ingestion.process_job(job1.job_id)

        # Reload job1 from DB
        job1_final = self.job_repository.get_job(job1.job_id)
        assert job1_final.status in [JobStatus.COMPLETED, JobStatus.FAILED], (
            f"First job should be COMPLETED or FAILED, got {job1_final.status}"
        )

        # 2. Second ingestion: Same URL should be SKIPPED
        job2 = self.ingestion.create_job(url=test_url)
        await self.ingestion.process_job(job2.job_id)

        # Reload job2 from DB
        job2_final = self.job_repository.get_job(job2.job_id)

        # Assertions
        assert job2_final.status == JobStatus.SKIPPED, f"Second job should be SKIPPED, got {job2_final.status}"
        assert job2_final.skip_reason is not None, "Skip reason should be set"
        assert "duplicate" in job2_final.skip_reason.lower() or "Duplicate" in job2_final.skip_reason, (
            f"Skip reason should mention 'duplicate', got: {job2_final.skip_reason}"
        )

    @pytest.mark.asyncio
    async def test_force_refresh_bypasses_deduplication(self):
        """
        [Spec 072] Test: force_refresh=True로 호출하면 중복 체크를 우회하고 재수집함
        """
        test_url = "https://example.com/test-force-refresh"

        # 1. First ingestion
        job1 = self.ingestion.create_job(url=test_url)
        await self.ingestion.process_job(job1.job_id)

        job1_final = self.job_repository.get_job(job1.job_id)
        assert job1_final.status in [JobStatus.COMPLETED, JobStatus.FAILED]

        # 2. Second ingestion WITHOUT force_refresh: Should SKIP
        job2 = self.ingestion.create_job(url=test_url)
        await self.ingestion.process_job(job2.job_id)

        job2_final = self.job_repository.get_job(job2.job_id)
        assert job2_final.status == JobStatus.SKIPPED, "Second job without force_refresh should be SKIPPED"

        # 3. Third ingestion WITH force_refresh: Should PROCEED
        job3 = self.ingestion.create_job(url=test_url)
        await self.ingestion.process_job(job3.job_id, force_refresh=True)

        job3_final = self.job_repository.get_job(job3.job_id)

        # Assertions
        assert job3_final.status != JobStatus.SKIPPED, (
            f"Third job with force_refresh should NOT be SKIPPED, got {job3_final.status}"
        )
        assert job3_final.status in [JobStatus.COMPLETED, JobStatus.FAILED], (
            f"Third job should be COMPLETED or FAILED, got {job3_final.status}"
        )

        # Content hash should be calculated
        assert job3_final.content_hash is not None, "Content hash should be calculated for force-refreshed job"

    @pytest.mark.asyncio
    async def test_skip_reason_persisted_in_database(self):
        """
        [Spec 072] Test: skip_reason이 데이터베이스에 정상적으로 저장되는지 확인
        """
        test_url = "https://example.com/test-skip-reason"

        # 1. First ingestion
        job1 = self.ingestion.create_job(url=test_url)
        await self.ingestion.process_job(job1.job_id)

        # 2. Second ingestion: Should be skipped with reason
        job2 = self.ingestion.create_job(url=test_url)
        await self.ingestion.process_job(job2.job_id)

        # 3. Verify skip_reason is persisted
        job2_from_db = self.job_repository.get_job(job2.job_id)

        assert job2_from_db.status == JobStatus.SKIPPED
        assert job2_from_db.skip_reason is not None
        assert len(job2_from_db.skip_reason) > 0

        # Verify skip_reason contains strategy name or job ID
        assert any(keyword in job2_from_db.skip_reason for keyword in ["job", "Duplicate", "Strategy"]), (
            f"Skip reason should contain meaningful info, got: {job2_from_db.skip_reason}"
        )
