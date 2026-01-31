import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.domain.value_objects.chunk import Chunk
from app.domain.entities.document import Document
from app.domain.services.chunker import Chunker


class LangChainChunker(Chunker):
    def __init__(self):
        self.settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
            add_start_index=True,
        )

    def chunk_document(self, document: Document) -> list[Chunk]:
        """문서를 재귀적으로 분할하여 Chunk 리스트를 반환합니다."""

        # LangChain의 create_documents를 사용하여 메타데이터 자동 처리 (start_index 등)
        lc_docs = self.splitter.create_documents([document.content], metadatas=[document.metadata])

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
                    "chunk_overlap": self.settings.CHUNK_OVERLAP,
                },
            )
            chunks.append(chunk)

        return chunks
