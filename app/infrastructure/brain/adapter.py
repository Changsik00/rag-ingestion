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

    def __init__(self, llm: LLMInterface):
        # We need an inner LLM to perform the actual extraction node logic
        self.llm = llm

        # Build the Graph
        builder = IngestionGraphBuilder(llm=llm)
        self.graph = builder.build()

    def extract_metadata(self, text: str) -> ExtractedMetadata | None:
        """
        Executes the ingestion graph to extract metadata from the text.

        Args:
            text: Raw content to analyze

        Returns:
            ExtractedMetadata: Extracted metadata
            None: If extraction fails
        """
        # 1. Initialize State
        initial_state = {
            "original_url": "",  # Optional, not used in extraction logic yet
            "raw_content": text,
            "metadata": {},
            "extracted_entities": [],
            "steps_history": [],
            "error": None,
            "retry_count": 0,
        }

        try:
            logger.info("Executing Ingestion Graph...")

            # 2. Invoke Graph
            # LangGraph CompiledGraph is a Runnable, invoking it is synchronous/blocking unless ainvoke is used.
            # Since LLMInterface.extract_metadata is sync, we use invoke.
            final_state = self.graph.invoke(initial_state)

            # 3. Extract Result from State
            metadata_dict = final_state.get("metadata")
            if not metadata_dict:
                logger.warning("Graph completed but no metadata found in state.")
                return None

            # 4. Convert back to Pydantic
            # Validation happens here. If metadata_dict is incomplete, it might raise ValidationError.
            # Ideally IngestionNodes ensures valid structure.
            return ExtractedMetadata(**metadata_dict)

        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            return None
