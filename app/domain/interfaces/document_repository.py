from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.document import Document
from app.domain.entities.chunk import Chunk


class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> None:
        """Persist a document."""
        pass

    @abstractmethod
    def save_with_chunks(self, document: Document, chunks: List[Chunk]) -> None:
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
