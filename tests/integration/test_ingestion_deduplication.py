import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from app.domain.entities.job import IngestionJob, JobStatus
from app.application.services.ingestion import Ingestion
from app.application.services.deduplication_strategies import DeduplicationStrategy

@pytest.fixture
def mock_components():
    return {
        "scraper": AsyncMock(),
        "repository": Mock(),
        "graph": Mock(),
        "job_repository": Mock(),
        "chunker": Mock(),
        "extractor": AsyncMock(),
    }

class TestIngestionDeduplication:
    
    @pytest.mark.asyncio
    async def test_process_job_skips_when_duplicate_detected(self, mock_components):
        # Given
        ingestion = Ingestion(**mock_components)
        job_id = "job-dup"
        job = IngestionJob(
            job_id=job_id,
            source_url="http://example.com/dup",
            status=JobStatus.PENDING
        )
        mock_components["job_repository"].get_job.return_value = job
        
        # Mock Deduplication Factory to return a Strategy that says "True" (Duplicate)
        mock_strategy = AsyncMock(spec=DeduplicationStrategy)
        mock_strategy.is_duplicate.return_value = True
        
        with patch("app.application.services.ingestion.DeduplicationFactory") as MockFactory:
            MockFactory.return_value.get_strategy.return_value = mock_strategy
            
            # When
            await ingestion.process_job(job_id)
            
            # Then
            # 1. Strategy was checked
            mock_strategy.is_duplicate.assert_awaited_once_with(job)
            
            # 2. Scraper was NOT called
            mock_components["scraper"].scrape.assert_not_called()
            
            # 3. Job status updated to SKIPPED (or COMPLETED with note? Let's assume SKIPPED for now as per plan)
            # Actually, IngestionJob status enum might needed 'SKIPPED' or we use 'COMPLETED'
            # The plan said "status=skipped"
            # But JobStatus Enum might not have SKIPPED. checking entities/job.py...
            # PENDING, RUNNING, COMPLETED, FAILED.
            # I need to add SKIPPED to Enum first! Or use COMPLETED.
            # Plan said "status=skipped". I should check Enum.
            
            # Assuming I will add SKIPPED to Enum in implementation.
            # Asserting call to update_job has status='SKIPPED'
            
            # Wait, if Enum doesn't have SKIPPED, this test will error in runtime if validition is strong, 
            # or logic will fail.
            # I will assume I add SKIPPED to Enum.
            
            args, _ = mock_components["job_repository"].update_job.call_args
            updated_job = args[0]
            assert updated_job.status == "SKIPPED" # or JobStatus.SKIPPED

    @pytest.mark.asyncio
    async def test_process_job_runs_when_not_duplicate(self, mock_components):
        # Given
        ingestion = Ingestion(**mock_components)
        job_id = "job-new"
        job = IngestionJob(job_id=job_id, source_url="http://example.com/new", status=JobStatus.PENDING)
        mock_components["job_repository"].get_job.return_value = job
        
        # Scraper returns dummy result
        mock_components["scraper"].scrape.return_value = Mock(markdown="content", metadata={})

        mock_strategy = AsyncMock(spec=DeduplicationStrategy)
        mock_strategy.is_duplicate.return_value = False
        
        with patch("app.application.services.ingestion.DeduplicationFactory") as MockFactory:
            MockFactory.return_value.get_strategy.return_value = mock_strategy
            
            # When
            await ingestion.process_job(job_id)
            
            # Then
            mock_strategy.is_duplicate.assert_awaited_once()
            mock_components["scraper"].scrape.assert_awaited_once()
            
            args, _ = mock_components["job_repository"].update_job.call_args_list[-1]
            assert args[0].status == JobStatus.COMPLETED
