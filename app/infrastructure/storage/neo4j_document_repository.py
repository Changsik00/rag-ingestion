import json
from uuid import UUID

from neo4j import Driver

from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository


class Neo4jStorage(DocumentRepository):
    def __init__(self, driver: Driver):
        self.driver = driver

    def close(self):
        self.driver.close()

    def save(self, document: AtomicDocument) -> None:
        # Neo4j는 중첩된 map을 지원하지 않으므로 metadata를 평탄화
        # 속성 값으로 primitive 타입(str, int, float, bool)과 배열만 허용됨
        flattened_metadata = {}

        for key, value in document.metadata.items():
            if isinstance(value, (dict, list)):
                # 복잡한 타입은 JSON 문자열로 직렬화
                flattened_metadata[f"{key}_json"] = json.dumps(value)
            else:
                # Primitive 타입은 그대로 유지
                flattened_metadata[key] = value

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
                metadata=flattened_metadata
            )

    def get(self, doc_id: UUID) -> AtomicDocument | None:
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

    def list_documents(self, limit: int = 10) -> list[AtomicDocument]:
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
