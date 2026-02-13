from unittest.mock import AsyncMock, patch
import pytest
from app.interfaces.tools.discovery_tool import DiscoveryTool

@pytest.mark.asyncio
async def test_discovery_tool_execution():
    with patch("app.interfaces.api.dependencies.get_neo4j_driver"), \
         patch("app.interfaces.api.dependencies.get_scraper"), \
         patch("app.interfaces.api.dependencies.get_repository"), \
         patch("app.interfaces.api.dependencies.get_graph_repository"), \
         patch("app.interfaces.api.dependencies.get_job_repository"), \
         patch("app.interfaces.api.dependencies.get_chunker"), \
         patch("app.interfaces.api.dependencies.get_google_search_client") as mock_get_client, \
         patch("app.domain.services.discovery_service.DiscoveryService") as MockService, \
         patch("app.application.services.ingestion.Ingestion"), \
         patch("app.application.saga.ingestion_handlers.IngestionSagaHandlers"):
        
        # Mock Service
        service_instance = AsyncMock()
        service_instance.start_discovery.return_value = ["job-1", "job-2"]
        MockService.return_value = service_instance
        
        tool = DiscoveryTool()
        result = await tool._arun("test topic")
        
        assert "Started 2 jobs" in result
        assert "job-1, job-2" in result
        service_instance.start_discovery.assert_called_once()
