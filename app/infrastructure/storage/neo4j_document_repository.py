import json
from uuid import UUID

from neo4j import Driver

from app.core.exceptions import InfrastructureException
from app.core.logging_config import setup_logger
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import DocumentRepository

logger = setup_logger(__name__)


class Neo4jStorage(DocumentRepository):
    def __init__(self, driver: Driver):
        self.driver = driver

    def close(self):
        self.driver.close()

    def _flatten_metadata(self, metadata: dict) -> dict:
        """Neo4j 호환을 위해 메타데이터 평탄화"""
        flattened = {}
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                flattened[f"{key}_json"] = json.dumps(value)
            else:
                flattened[key] = value
        return flattened

    def save(self, document: Document) -> None:
        try:
            flattened_metadata = self._flatten_metadata(document.metadata)

            query = """
            MERGE (d:Document {id: $id})
            SET d.content = $content,
                d.created_at = $created_at,
                d += $metadata
            """
            # source_url is now part of metadata or handled if it exists,
            # but legacy AtomicDocument had it explicit.
            # Our new Document entity removed source_url and put it in metadata?
            # Let's check Document entity definition again.
            # Document entity has `content` and `metadata`. `source_url` was removed from field list in my edit?
            # Yes, I removed explicit `source_url` field in Step 181.
            # I must ensure it is saved in metadata if present.

            with self.driver.session() as session:
                session.run(
                    query,
                    id=str(document.id),
                    content=document.content,
                    created_at=document.created_at.isoformat(),
                    metadata=flattened_metadata,
                )
        except Exception as e:
            logger.error(f"Failed to save document to Neo4j: {e}")
            raise InfrastructureException(f"Failed to save document to Neo4j: {e}") from e

    def save_with_chunks(self, document: Document, chunks: list[Chunk]) -> None:
        """문서와 청크를 함께 저장하고 관계를 형성합니다."""
        try:
            # 1. 문서 저장 (기존 로직 재사용 가능하거나 통합)
            self.save(document)

            # 2. 청크 저장 및 관계 생성
            query = """
            MATCH (d:Document {id: $doc_id})
            UNWIND $chunks AS chunk_data
            MERGE (c:Chunk {id: chunk_data.id})
            SET c.content = chunk_data.content,
                c.index = chunk_data.index,
                c.parent_id = $doc_id,
                c += chunk_data.metadata
            MERGE (d)-[:HAS_CHUNK]->(c)
            """

            # Prepare chunks data
            chunks_data = []
            for chunk in chunks:
                chunk_dict = {
                    "id": chunk.id,
                    "content": chunk.content,
                    "index": chunk.index,
                    "metadata": self._flatten_metadata(chunk.metadata),
                }
                chunks_data.append(chunk_dict)

            with self.driver.session() as session:
                session.run(query, doc_id=document.id, chunks=chunks_data)

        except Exception as e:
            logger.error(f"Failed to save chunks to Neo4j: {e}")
            raise InfrastructureException(f"Failed to save chunks to Neo4j: {e}") from e

    def get(self, doc_id: UUID) -> Document | None:
        try:
            query = "MATCH (d:Document {id: $id}) RETURN d"
            with self.driver.session() as session:
                result = session.run(query, id=str(doc_id)).single()
                if result:
                    node = result["d"]
                    return Document(
                        id=UUID(node["id"]) if isinstance(node["id"], str) else node["id"],  # Handle ID type safely
                        content=node.get("content", ""),
                        # source_url removal handled by not mapping it explicitly
                        metadata={k: v for k, v in node.items() if k not in ["id", "content", "created_at"]},
                        created_at=node.get("created_at"),  # Pydantic will handle parsing if isoformat string
                    )
            return None
        except Exception as e:
            logger.error(f"Failed to get document from Neo4j (id={doc_id}): {e}")
            raise InfrastructureException(f"Failed to get document from Neo4j: {e}") from e

    def list_documents(self, limit: int = 10) -> list[Document]:
        try:
            query = "MATCH (d:Document) RETURN d LIMIT $limit"
            docs = []
            with self.driver.session() as session:
                results = session.run(query, limit=limit)
                for record in results:
                    node = record["d"]
                    docs.append(
                        Document(
                            id=node["id"],  # Pydantic handles str->str
                            content=node.get("content", ""),
                            metadata={k: v for k, v in node.items() if k not in ["id", "content", "created_at"]},
                        )
                    )
            return docs
        except Exception as e:
            logger.error(f"Failed to list documents from Neo4j: {e}")
            raise InfrastructureException(f"Failed to list documents from Neo4j: {e}") from e
