import logging
import uuid
from typing import Any

from langchain_core.messages import AIMessage

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

    async def list_threads(self, limit: int = 50) -> list[Any]:
        """List active threads using checkpointer."""
        if not self.graph.checkpointer:
            return []
        return [t async for t in self.graph.checkpointer.alist(None, limit=limit)]

    async def get_thread_status(self, thread_id: str) -> str:
        """Get status of a specific thread."""
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = await self.graph.aget_state(config)
        return "INTERRUPTED" if snapshot.next else "COMPLETED"

    async def get_state(self, thread_id: str) -> Any:
        """Get full state for a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        return await self.graph.aget_state(config)

    async def resume(self, thread_id: str, user_input: Any) -> dict:
        """Resume interrupted workflow with human feedback."""
        config = {"configurable": {"thread_id": thread_id}}
        # Spec 022: Manual update state before resume
        await self.graph.aupdate_state(config, {"error": None, "messages": [AIMessage(content=f"Human Feedback: {user_input}")]}, as_node="human_review")
        return await self.graph.ainvoke(None, config=config)

    async def reset_checkpoints(self) -> None:
        """Truncate all checkpoints (Admin use only)."""
        if self.graph.checkpointer:
            # Assuming PostgresSaver
            conn = getattr(self.graph.checkpointer, "conn", None)
            if conn:
                await conn.execute("TRUNCATE checkpoints RESTART IDENTITY CASCADE;")
                await conn.commit()
                logger.info("Checkpoints truncated successfully.")
