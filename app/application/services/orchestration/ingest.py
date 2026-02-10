import logging
import uuid
from typing import Any

from app.domain.value_objects.extracted_metadata import ExtractedMetadata

logger = logging.getLogger(__name__)


class IngestOrchestrator:
    """
    Orchestration Layer for Ingest: Coordinates the metadata extraction flow.
    Replaces the IngestionOrchestrator infrastructure class.
    """

    def __init__(self, graph_builder: Any):
        """
        Args:
            graph_builder: Infrastructure component that knows how to build the LangGraph.
        """
        self.graph = graph_builder.build()

    async def aextract_metadata(
        self, text: str, metadata: dict | None = None, thread_id: str | None = None
    ) -> ExtractedMetadata | None:
        """
        Executes the ingestion workflow to extract metadata from the text.
        """
        actual_thread_id = thread_id
        if self.graph.checkpointer and not actual_thread_id:
            actual_thread_id = f"auto-{uuid.uuid4()}"
            logger.info(f"Checkpointer active but no thread_id provided. Using auto-generated: {actual_thread_id}")

        config = {"configurable": {"thread_id": actual_thread_id}} if actual_thread_id else None

        initial_state = {
            "original_url": "",
            "raw_content": text,
            "content_metadata": metadata or {},
            "metadata": None,
            "messages": [],
            "error": None,
            "retry_count": 0,
        }

        try:
            logger.info(f"Executing Ingestion Workflow (Thread: {actual_thread_id})...")
            final_state = await self.graph.ainvoke(initial_state, config=config)

            if thread_id:
                snapshot = await self.graph.aget_state(config)
                if snapshot.next:
                    logger.info(f"Workflow execution interrupted (HITL required) for thread {thread_id}")
                    return None

            return final_state.get("metadata")

        except Exception as e:
            logger.error(f"Ingestion workflow failed: {e}")
            return None

    async def cleanup_thread(self, thread_id: str) -> None:
        """Clean up thread history."""
        if self.graph.checkpointer and hasattr(self.graph.checkpointer, "adelete_thread"):
            try:
                await self.graph.checkpointer.adelete_thread(thread_id)
                logger.info(f"Cleanup: History for thread {thread_id} deleted.")
            except Exception as e:
                logger.error(f"Cleanup failed for thread {thread_id}: {e}")
