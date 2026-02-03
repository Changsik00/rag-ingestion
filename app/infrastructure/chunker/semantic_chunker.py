import uuid

from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import get_settings
from app.domain.entities.document import Document
from app.domain.interfaces.chunker import Chunker
from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.chunk_config import ChunkingConfig


class LangChainSemanticChunker(Chunker):
    def __init__(self, config: ChunkingConfig | None = None):
        self.settings = get_settings()
        self.config = config or ChunkingConfig(strategy="semantic")

        # Initialize embeddings (using Gemini as default in this project)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.settings.GEMINI_EMBEDDING_MODEL_NAME,
            google_api_key=self.settings.GEMINI_API_KEY,
        )

        # Initialize LangChain SemanticChunker
        self.splitter = SemanticChunker(
            buffer_size=1,  # Default buffer size for sentence grouping
            embeddings=self.embeddings,
            breakpoint_threshold_type=self.config.breakpoint_threshold_type,
            breakpoint_threshold_amount=self.config.breakpoint_threshold_amount,
            number_of_chunks=self.config.number_of_chunks,
        )

    def chunk_document(self, document: Document) -> list[Chunk]:
        """문서를 의미상 유사성에 따라 분할하여 Chunk 리스트를 반환합니다."""

        metadatas = [document.metadata.model_dump() if hasattr(document.metadata, "model_dump") else document.metadata]
        lc_docs = self.splitter.create_documents([document.content], metadatas=metadatas)

        chunks = []
        for i, lc_doc in enumerate(lc_docs):
            chunk = Chunk(
                id=str(uuid.uuid4()),
                content=lc_doc.page_content,
                parent_id=document.id,
                index=i,
                metadata={
                    **lc_doc.metadata,
                    "chunk_size": len(lc_doc.page_content),
                    "chunking_strategy": "semantic",
                    "threshold_type": self.config.breakpoint_threshold_type,
                    "threshold_amount": self.config.breakpoint_threshold_amount,
                },
            )
            chunks.append(chunk)

        return chunks
