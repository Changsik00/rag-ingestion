from uuid import UUID

from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository


class CompositeStorage(DocumentRepository):
    """
    여러 저장소를 조합하여 사용하는 Composite 패턴 구현
    
    Document를 Graph DB(Neo4j)와 Vector DB(ChromaDB)에 동시 저장하여
    구조화된 쿼리와 의미 기반 검색을 모두 지원합니다.
    
    Args:
        neo4j: 구조화된 데이터 저장용 DocumentRepository (Neo4j)
        chroma: 벡터 임베딩 저장용 DocumentRepository (ChromaDB)
    """
    def __init__(self, neo4j: DocumentRepository, chroma: DocumentRepository):
        self.neo4j = neo4j
        self.chroma = chroma

    def save(self, document: AtomicDocument) -> None:
        # Graph DB에 저장 (구조 및 메타데이터)
        self.neo4j.save(document)
        # Vector DB에 저장 (임베딩)
        self.chroma.save(document)

    def get(self, doc_id: UUID) -> AtomicDocument | None:
        # Primary 검색 소스는 Neo4j
        return self.neo4j.get(doc_id)

    def list_documents(self, limit: int = 10) -> list[AtomicDocument]:
        return self.neo4j.list_documents(limit)
