from abc import ABC, abstractmethod

from app.domain.entities.document import Document
from app.domain.value_objects.chunk import Chunk


class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> None:
        """Persist a document."""
        pass

    @abstractmethod
    def save_with_chunks(self, document: Document, chunks: list[Chunk]) -> None:
        """Persist a document and its chunks."""
        pass

    @abstractmethod
    def get(self, doc_id: str) -> Document | None:
        """Retrieve a document by ID."""
        pass

    @abstractmethod
    def list_documents(self, limit: int = 10, search_term: str | None = None) -> list[Document]:
        """List recently stored documents."""
        pass

    @abstractmethod
    def get_chunks(self, doc_id: str) -> list[Chunk]:
        """Retrieve all chunks for a document."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        """
        Search for relevant chunks.
        :param query: Search query string.
        :param limit: Maximum number of results.
        :param filters: Metadata filters (e.g., {"doc_id": "..."} or {"doc_id": ["...", ...]}).
        """
        pass

    @abstractmethod
    def get_all_chunk_ids(self) -> set[str]:
        """Retrieve all chunk IDs in the storage."""
        pass

    @abstractmethod
    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[Chunk]:
        """Retrieve multiple chunks by their IDs."""
        pass

    @abstractmethod
    def get_document_stats(self) -> list[dict]:
        """Retrieve high-level statistics per document."""
        pass

    @abstractmethod
    def get_adjacent_chunks(self, parent_id: str, index: int, window_size: int = 1) -> list[Chunk]:
        """
        Retrieve adjacent chunks for a given chunk index within the same document.
        :param parent_id: The ID of the parent document.
        :param index: The index of the pivot chunk.
        :param window_size: Number of chunks to fetch before and after.
        """
        pass
