from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document


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
    def get(self, doc_id: UUID) -> Document | None:
        """Retrieve a document by ID."""
        pass

    @abstractmethod
    def list_documents(self, limit: int = 10) -> list[Document]:
        """List recently stored documents."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[Chunk]:
        """Search for relevant chunks."""
        pass
