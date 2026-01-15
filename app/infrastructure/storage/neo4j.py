from typing import List, Optional
from uuid import UUID
from neo4j import GraphDatabase
from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository
import os

class Neo4jStorage(DocumentRepository):
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def save(self, document: AtomicDocument) -> None:
        query = """
        MERGE (d:Document {id: $id})
        SET d.content = $content,
            d.source_url = $source_url,
            d.created_at = $created_at,
            d += $metadata
        """
        with self.driver.session() as session:
            session.run(query, 
                id=str(document.id),
                content=document.content,
                source_url=document.source_url,
                created_at=document.created_at.isoformat(),
                metadata=document.metadata
            )

    def get(self, doc_id: UUID) -> Optional[AtomicDocument]:
        query = "MATCH (d:Document {id: $id}) RETURN d"
        with self.driver.session() as session:
            result = session.run(query, id=str(doc_id)).single()
            if result:
                node = result["d"]
                return AtomicDocument(
                    id=UUID(node["id"]),
                    content=node.get("content", ""),
                    source_url=node.get("source_url", ""),
                    metadata={k:v for k,v in node.items() if k not in ["id", "content", "source_url", "created_at"]}
                )
        return None

    def list_documents(self, limit: int = 10) -> List[AtomicDocument]:
        query = "MATCH (d:Document) RETURN d LIMIT $limit"
        docs = []
        with self.driver.session() as session:
            results = session.run(query, limit=limit)
            for record in results:
                node = record["d"]
                docs.append(AtomicDocument(
                    id=UUID(node["id"]),
                    content=node.get("content", ""),
                    source_url=node.get("source_url", ""),
                    metadata={k:v for k,v in node.items() if k not in ["id", "content", "source_url", "created_at"]}
                ))
        return docs
