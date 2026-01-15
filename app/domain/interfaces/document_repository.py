from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.document import AtomicDocument

class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: AtomicDocument) -> None:
        """Persist a document."""
        pass

    @abstractmethod
    def get(self, doc_id: UUID) -> Optional[AtomicDocument]:
        """Retrieve a document by ID."""
        pass

    @abstractmethod
    def list_documents(self, limit: int = 10) -> List[AtomicDocument]:
        """List recently stored documents."""
        pass
