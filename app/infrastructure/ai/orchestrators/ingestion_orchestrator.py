import logging

from app.application.interfaces.llm import LLMInterface
from app.domain.value_objects.extracted_metadata import ExtractedMetadata
from app.infrastructure.ai.graphs.ingestion_graph import IngestionGraphBuilder

logger = logging.getLogger(__name__)


class IngestionOrchestrator:
    """
    LLMInterface implementation that orchestrates the extraction via LangGraph.
    Acts as the new entry point for Domain Service, replacing direct LangChain calls.
    """

    def __init__(self, llm: LLMInterface, checkpointer=None):
        # We need an inner LLM to perform the actual extraction node logic
        self.llm = llm

        # Build the Graph
        builder = IngestionGraphBuilder(llm=llm)
        self.graph = builder.build(checkpointer=checkpointer)

    async def aextract_metadata(self, text: str, thread_id: str | None = None) -> ExtractedMetadata | None:
        """
        Executes the ingestion graph to extract metadata from the text.

        Args:
            text: Raw content to analyze
            thread_id: Optional thread ID for persistence (HITL)

        Returns:
            ExtractedMetadata: Extracted metadata
            None: If extraction fails or is interrupted
        """
        # 1. Initialize State
        config = None
        # Spec 040 Fix: If checkpointer is present but thread_id is missing, generate a dummy one to avoid error
        actual_thread_id = thread_id
        if self.graph.checkpointer and not actual_thread_id:
            import uuid

            actual_thread_id = f"auto-{uuid.uuid4()}"
            logger.info(f"Checkpointer active but no thread_id provided. Using auto-generated: {actual_thread_id}")

        if actual_thread_id:
            config = {"configurable": {"thread_id": actual_thread_id}}

        initial_state = {
            "original_url": "",  # Optional, not used in extraction logic yet
            "raw_content": text,
            "metadata": None,
            "steps_history": [],
            "error": None,
            "retry_count": 0,
        }

        try:
            logger.info(f"Executing Ingestion Graph (Thread: {actual_thread_id})...")

            # 2. Invoke Graph (Async)
            final_state = await self.graph.ainvoke(initial_state, config=config)

            # Check for interrupt/next steps (HITL)
            if thread_id:
                snapshot = await self.graph.aget_state(config)
                if snapshot.next:
                    logger.info(f"Graph execution interrupted (HITL required) for thread {thread_id}")
                    return None

            # 3. Extract Result from State
            metadata = final_state.get("metadata")
            return metadata

        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            return None

    async def get_state(self, thread_id: str):
        """Get the current state of a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        return await self.graph.aget_state(config)

    async def resume(self, thread_id: str, input_data: dict):
        """Resume execution of a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        # Spec 022 used interrupt_before=["human_review"].
        # For simple resume:
        return await self.graph.ainvoke(input_data, config=config)

    async def get_thread_status(self, thread_id: str) -> str:
        snapshot = await self.get_state(thread_id)
        if not snapshot.values:
            return "Empty"
        if snapshot.next:
            return "Interrupted"
        return "Completed"

    async def list_threads(self, limit: int = 10):
        """List persistent threads."""
        if not self.graph.checkpointer:
            return []

        # Async Checkpointer uses alist
        threads = []
        async for t in self.graph.checkpointer.alist(None, limit=limit):
            threads.append(t)
        return threads

    async def reset_checkpoints(self):
        """Reset the checkpointer (SQLite) by clearing all state data."""
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        if self.graph.checkpointer and isinstance(self.graph.checkpointer, AsyncSqliteSaver):
            try:
                # AsyncSqliteSaver has .conn attribute which is aiosqlite connection
                async with self.graph.checkpointer.conn.execute("DELETE FROM checkpoints") as _:
                    pass
                async with self.graph.checkpointer.conn.execute("DELETE FROM checkpoint_blobs") as _:
                    pass
                async with self.graph.checkpointer.conn.execute("DELETE FROM checkpoint_writes") as _:
                    pass
                await self.graph.checkpointer.conn.commit()
                logger.warning("LangGraph Adapter: Checkpoints have been reset (SQLite tables cleared).")
            except Exception as e:
                logger.error(f"Failed to reset LangGraph checkpoints: {e}")
                # Don't raise, just log. It might be empty or locked.
        else:
            logger.info("LangGraph Adapter: No AsyncSqliteSaver checkpointer found to reset.")
