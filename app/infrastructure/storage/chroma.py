from typing import List, Optional
from uuid import UUID
import chromadb
from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository
import os

class ChromaStorage(DocumentRepository):
    def __init__(self):
        host = os.getenv("CHROMA_HOST", "localhost")
        port = os.getenv("CHROMA_PORT", "8000")
        self.client = chromadb.HttpClient(host=host, port=int(port))
        self.collection = self.client.get_or_create_collection(name="documents")

    def save(self, document: AtomicDocument) -> None:
        self.collection.add(
            documents=[document.content],
            metadatas=[{"source_url": document.source_url, **document.metadata}],
            ids=[str(document.id)]
        )

    def get(self, doc_id: UUID) -> Optional[AtomicDocument]:
        # Chroma is less suitable for primary retrieval, but consistent interface requires it.
        # Minimal implementation for now.
        result = self.collection.get(ids=[str(doc_id)])
        if result and result['documents']:
             # Reconstructing object from Chroma is lossy (no full metadata usually), 
             # but we implement basic mapping.
             return AtomicDocument(
                 id=doc_id,
                 content=result['documents'][0],
                 source_url=result['metadatas'][0].get("source_url", ""),
                 metadata=result['metadatas'][0]
             )
        return None

    def list_documents(self, limit: int = 10) -> List[AtomicDocument]:
        # Chroma peek
        result = self.collection.peek(limit=limit)
        docs = []
        if result and result['ids']:
            for i in range(len(result['ids'])):
                 docs.append(AtomicDocument(
                     id=UUID(result['ids'][i]),
                     content=result['documents'][i],
                     source_url=result['metadatas'][i].get("source_url", ""),
                     metadata=result['metadatas'][i]
                 ))
        return docs
