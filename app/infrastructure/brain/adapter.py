import logging

from app.domain.interfaces.llm import LLMInterface
from app.domain.schemas.extraction import ExtractedMetadata
from app.infrastructure.brain.graph import IngestionGraphBuilder

logger = logging.getLogger(__name__)


class LangGraphAdapter:
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

    async def extract_metadata(self, text: str, thread_id: str | None = None) -> ExtractedMetadata | None:
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
        if thread_id:
            config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "original_url": "",  # Optional, not used in extraction logic yet
            "raw_content": text,
            "metadata": None,
            "steps_history": [],
            "error": None,
            "retry_count": 0,
        }

        try:
            logger.info(f"Executing Ingestion Graph (Thread: {thread_id})...")

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
