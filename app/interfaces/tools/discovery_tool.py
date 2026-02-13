import logging
from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class DiscoveryInput(BaseModel):
    topic: str = Field(description="The topic to research and discover")
    max_depth: int = Field(default=1, description="How deep to crawl recursively (0-3)")
    max_docs: int = Field(default=5, description="Maximum number of documents to collect")

class DiscoveryTool(BaseTool):
    name: str = "autonomous_discovery"
    description: str = (
        "Use this tool to research a topic by searching Google and recursively crawling websites. "
        "Useful when you need to gather broad knowledge about a subject from the web. "
        "It will trigger ingestion jobs and return a summary of started jobs."
    )
    args_schema: Type[BaseModel] = DiscoveryInput

    def _run(self, topic: str, max_depth: int = 1, max_docs: int = 5) -> str:
        """Synchronous run is not supported for this async tool."""
        raise NotImplementedError("This tool strictly requires async execution.")

    async def _arun(self, topic: str, max_depth: int = 1, max_docs: int = 5) -> str:
        try:
            logger.info(f"Tool autonomous_discovery called with topic={topic}")
            
            # Manual Dependency Injection for execution context
            from app.interfaces.api.dependencies import (
                get_google_search_client,
                get_scraper,
                get_repository,
                get_graph_repository,
                get_job_repository,
                get_chunker,
                get_neo4j_driver
            )
            from app.application.services.ingestion import Ingestion
            from app.domain.services.discovery_service import DiscoveryService
            from app.application.saga.ingestion_handlers import IngestionSagaHandlers

            # 1. Resolve Dependencies
            driver = get_neo4j_driver()
            
            scraper = get_scraper()
            repo = get_repository()
            graph = get_graph_repository(driver)
            job_repo = get_job_repository(driver)
            chunker = get_chunker()
            
            # Note: We omit SemanticExtractor in this manual composition 
            # because valid ingestion usually goes through API which sets up EVERYTHING.
            # But here we just need detailed enough Ingestion service to create jobs.
            # The actual PROCESSING happens in Background Tasks via EventBus, 
            # so as long as EventBus is running, we are fine.
            
            # Initialize Saga Handlers if not already done (Idempotent)
            # IngestionSagaHandlers.initialize() might be needed if this runs in isolation.
            IngestionSagaHandlers.initialize(
                job_repository=job_repo,
                document_repository=repo,
                graph_repository=graph,
                scraper=scraper,
                extractor=None, # Extractor might be None here, assuming Worker handles it
                chunker=chunker
            )

            ingestion_service = Ingestion(
                scraper=scraper,
                repository=repo,
                graph=graph,
                job_repository=job_repo,
                chunker=chunker,
                extractor=None 
            )

            search_client = get_google_search_client()
            
            discovery_service = DiscoveryService(
                search_client=search_client,
                ingestion_service=ingestion_service
            )

            # 2. Execute Logic
            job_ids = await discovery_service.start_discovery(
                topic=topic,
                max_depth=max_depth,
                max_docs=max_docs
            )
            
            return f"Discovery started for '{topic}'. Started {len(job_ids)} jobs. Job IDs: {', '.join(job_ids)}"

        except Exception as e:
            logger.error(f"Discovery Tool failed: {e}", exc_info=True)
            return f"Error during discovery: {str(e)}"
