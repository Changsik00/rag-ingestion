from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.value_objects.chunk import Chunk


class CompositeDocumentRepository(DocumentRepository):
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

    def save(self, document: Document) -> None:
        # Graph DB에 저장 (구조 및 메타데이터)
        self.neo4j.save(document)
        # Vector DB에 저장 (임베딩)
        self.chroma.save(document)

    def save_with_chunks(self, document: Document, chunks: list[Chunk]) -> None:
        # Graph DB: 문서 + 청크 + 관계 저장
        self.neo4j.save_with_chunks(document, chunks)
        # Vector DB: 청크 임베딩 저장
        # Interface save_with_chunks 호출 (내부적으로 save_chunks 호출)
        self.chroma.save_with_chunks(document, chunks)

    def get(self, doc_id: str) -> Document | None:
        # Primary 검색 소스는 Neo4j
        return self.neo4j.get(doc_id)

    def list_documents(self, limit: int = 10, search_term: str | None = None) -> list[Document]:
        return self.neo4j.list_documents(limit, search_term=search_term)

    def get_chunks(self, doc_id: str) -> list[Chunk]:
        """Retrieve all chunks for a document."""
        return self.neo4j.get_chunks(doc_id)

    def search(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        return self.chroma.search(query, limit, filters=filters)

    def get_all_chunk_ids(self) -> set[str]:
        return self.neo4j.get_all_chunk_ids()

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[Chunk]:
        return self.neo4j.get_chunks_by_ids(chunk_ids)

    async def delete(self, doc_id: str) -> bool:
        """
        [Spec 076] Delete a document from both Neo4j and ChromaDB.
        """
        # 1. Delete from Neo4j
        neo4j_success = await self.neo4j.delete(doc_id)
            
        # 2. Delete from ChromaDB
        chroma_success = await self.chroma.delete(doc_id)
            
        return neo4j_success or chroma_success

    def get_document_stats(self) -> list[dict]:
        return self.neo4j.get_document_stats()

    def get_all_chunk_metadata(self) -> list[dict]:
        return self.neo4j.get_all_chunk_metadata()

    def get_adjacent_chunks(self, parent_id: str, index: int, window_size: int = 1) -> list[Chunk]:
        """
        인접 청크 조회를 위해 Neo4j 저장소를 사용합니다.
        Neo4j가 문서의 구조적 관계를 관리하는 Primary Source입니다.
        """
        return self.neo4j.get_adjacent_chunks(parent_id, index, window_size)
