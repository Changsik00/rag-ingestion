from app.domain.interfaces.chunker import Chunker
from app.domain.value_objects.chunk_config import ChunkingConfig, ChunkingStrategy
from app.infrastructure.chunker.langchain_chunker import LangChainChunker
from app.infrastructure.chunker.semantic_chunker import LangChainSemanticChunker


class ChunkerFactory:
    @staticmethod
    def get_chunker(config: ChunkingConfig | None = None) -> Chunker:
        config = config or ChunkingConfig()

        if config.strategy == ChunkingStrategy.SEMANTIC:
            return LangChainSemanticChunker(config=config)
        else:
            return LangChainChunker(config=config)
