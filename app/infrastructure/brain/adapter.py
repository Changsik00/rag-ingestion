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

    def extract_metadata(self, text: str, thread_id: str | None = None) -> ExtractedMetadata | None:
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

            # 2. Invoke Graph
            # LangGraph CompiledGraph is a Runnable, invoking it is synchronous/blocking unless ainvoke is used.
            # Since LLMInterface.extract_metadata is sync, we use invoke.
            final_state = self.graph.invoke(initial_state, config=config)

            # Check for interrupt/next steps (HITL)
            # If the graph stopped but didn't finish, we might be in interrupted state.
            # However, invoke() typically runs until end or interrupt.
            # If using checkpointer, we can inspect if it's really done.
            if thread_id:
                snapshot = self.graph.get_state(config)
                if snapshot.next:
                    logger.info(f"Graph execution interrupted (HITL required) for thread {thread_id}")
                    # We return None or raise Exception.
                    # Returning None will cause ingestion to log warning but proceed?
                    # We should probably let IngestionService know.
                    # For now, let's return None and let IngestionService handle "no metadata" logic.
                    return None

            # 3. Extract Result from State
            metadata = final_state.get("metadata")

            # Since we store Pydantic model directly now, we just return it
            return metadata

        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            return None

    def get_state(self, thread_id: str):
        """Get the current state of a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.get_state(config)

    def resume(self, thread_id: str, input_data: dict):
        """Resume execution of a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        # Depending on how the graph was interrupted, we might need to update state or just invoke with None via Command.
        # But commonly we just invoke with new input which merges or replaces?
        # If interrupted at 'human_review', we proceed to 'resolve_logic' usually.
        # We can pass Command(resume=value) or just update state.
        # Let's assume we invoke with Command(resume=input_data) if using interrupt_before?
        # Or if we just "Resume", we might use None.

        # Spec 022 used interrupt_before=["human_review"].
        # So we need to provide a Command or update state to satisfy the node?
        # Actually, if we just invoke(None, config), it might resume if state is ready.
        # But if we need user feedback, we might update state first.
        # For simple resume:
        return self.graph.invoke(input_data, config=config)

    def get_thread_status(self, thread_id: str) -> str:
        snapshot = self.get_state(thread_id)
        if not snapshot.values:
            return "Empty"
        if snapshot.next:
            return "Interrupted"  # or specific node name
        return "Completed"

    def list_threads(self, limit: int = 10):
        """List persistent threads."""
        if not self.graph.checkpointer:
            return []

        # Checkpointer.list returns iterator of CheckpointTuple?
        # Actually, BaseCheckpointSaver.list(config, before, limit)
        # We need to check langgraph documentation or source.
        # Assuming list(None, limit=limit) returns list of CheckpointTuples.
        # Each tuple has config.
        # config = {"configurable": {"thread_id": ""}} # Dummy config?
        # list() signature: (config: Optional[RunnableConfig], before: Optional[RunnableConfig] = None, limit: int = None)
        # It filters by config if provided. If None, listing might depend on implementation.
        # SqliteSaver.list(config, ...)
        # Let's try passing None.
        return list(self.graph.checkpointer.list(None, limit=limit))
