from enum import Enum
from pydantic import BaseModel, Field


class ChunkingStrategy(str, Enum):
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"


class ChunkingConfig(BaseModel):
    strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE

    # Parameters for RecursiveChunker
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Parameters for SemanticChunker
    # LangChain SemanticChunker supports: "percentile", "standard_deviation", "interquartile", "gradient"
    breakpoint_threshold_type: str = "percentile"
    breakpoint_threshold_amount: float = Field(default=90.0, description="Percentile threshold for splitting chunks")
    number_of_chunks: int | None = None
