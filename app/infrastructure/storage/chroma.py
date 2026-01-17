import json
import os
from uuid import UUID

import chromadb

from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository


class ChromaStorage(DocumentRepository):
    def __init__(self):
        host = os.getenv("CHROMA_HOST", "localhost")
        port = os.getenv("CHROMA_PORT", "8001")
        self.client = chromadb.HttpClient(host=host, port=int(port))
        self.collection = self.client.get_or_create_collection(name="documents")

    def save(self, document: AtomicDocument) -> None:
        # Flatten metadata to comply with ChromaDB constraints
        # ChromaDB only accepts str, int, float, bool as metadata values
        flattened_metadata = {"source_url": document.source_url}
        
        for key, value in document.metadata.items():
            if isinstance(value, (dict, list)):
                # Serialize complex types to JSON string
                flattened_metadata[f"{key}_json"] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool, type(None))):
                # Keep primitive types as-is
                flattened_metadata[key] = value
            # Skip other types that ChromaDB doesn't support
        
        self.collection.add(
            documents=[document.content],
            metadatas=[flattened_metadata],
            ids=[str(document.id)]
        )

    def get(self, doc_id: UUID) -> AtomicDocument | None:
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

    def list_documents(self, limit: int = 10) -> list[AtomicDocument]:
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
