from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.services.discovery_service import DiscoveryService
from app.infrastructure.external_api.google_search_client import SearchResult


@pytest.fixture
def mock_search_client():
    client = AsyncMock()
    client.search.return_value = [SearchResult(title="Test", link="http://example.com", snippet="Test")]
    return client


@pytest.fixture
def mock_ingestion_service():
    service = AsyncMock()
    job = MagicMock()
    job.job_id = "job-123"
    service.ingest_url.return_value = job
    return service


@pytest.fixture
def discovery_service(mock_search_client, mock_ingestion_service):
    return DiscoveryService(mock_search_client, mock_ingestion_service)


@pytest.mark.asyncio
async def test_start_discovery_flow(discovery_service, mock_search_client, mock_ingestion_service):
    # Mock _fetch_links to avoid real HTTP requests
    discovery_service._fetch_links = AsyncMock(return_value=["http://example.com/page1", "http://example.com/page2"])

    job_ids = await discovery_service.start_discovery("test topic", max_depth=1, max_docs=5)

    assert len(job_ids) > 0
    mock_search_client.search.assert_called_once_with("test topic", num_results=5)
    # Should ingest seed + links
    assert mock_ingestion_service.ingest_url.call_count >= 1


@pytest.mark.asyncio
async def test_blocklist(discovery_service):
    assert discovery_service._is_blocked("http://youtube.com/watch?v=123")
    assert discovery_service._is_blocked("http://example.com/file.pdf")
    assert not discovery_service._is_blocked("http://good-site.com/article")


@pytest.mark.asyncio
async def test_max_docs_limit(discovery_service, mock_ingestion_service):
    discovery_service._fetch_links = AsyncMock(return_value=[f"http://example.com/{i}" for i in range(20)])

    # max_docs 3
    await discovery_service.start_discovery("test", max_depth=1, max_docs=3)

    # Should not exceed 3 ingest calls
    assert mock_ingestion_service.ingest_url.call_count <= 3
