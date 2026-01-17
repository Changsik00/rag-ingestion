from uuid import UUID

from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository


class CompositeStorage(DocumentRepository):
    def __init__(self, neo4j: DocumentRepository, chroma: DocumentRepository):
        self.neo4j = neo4j
        self.chroma = chroma

    def save(self, document: AtomicDocument) -> None:
        # Save to Graph (Structure & Metadata)
        self.neo4j.save(document)
        # Save to Vector (Embedding)
        self.chroma.save(document)

    def get(self, doc_id: UUID) -> AtomicDocument | None:
        # Primary source for retrieval is Neo4j
        return self.neo4j.get(doc_id)

    def list_documents(self, limit: int = 10) -> list[AtomicDocument]:
        return self.neo4j.list_documents(limit)
