from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.document import AtomicDocument


class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: AtomicDocument) -> None:
        """Persist a document."""
        pass

    @abstractmethod
    def get(self, doc_id: UUID) -> AtomicDocument | None:
        """Retrieve a document by ID."""
        pass

    @abstractmethod
    def list_documents(self, limit: int = 10) -> list[AtomicDocument]:
        """List recently stored documents."""
        pass
