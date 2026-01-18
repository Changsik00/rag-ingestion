"""
Graph Repository Interface (Protocol)

Domain Layer에서 Knowledge Graph 저장소의 계약을 정의합니다.
Infrastructure Layer의 구현체(Neo4jGraphRepository)는 이 Protocol을 준수해야 합니다.
"""

from typing import Protocol

from app.domain.schemas.ontology import EntityType, TypedEntity


class GraphRepository(Protocol):
    """Knowledge Graph 저장소 인터페이스"""

    def save_entity(self, name: str, entity_type: EntityType) -> str:
        """
        Entity 노드 생성/조회 (MERGE)

        Args:
            name: Entity 이름 (예: "Elon Musk")
            entity_type: Entity 타입 (EntityType enum)

        Returns:
            저장된 Entity의 name
        """
        ...

    def create_mention_relationship(
        self,
        doc_id: str,
        entity_name: str
    ) -> None:
        """
        Document-Entity MENTIONS 관계 생성

        Args:
            doc_id: Document ID (UUID 문자열)
            entity_name: Entity 이름
        """
        ...

    def get_entities_by_document(self, doc_id: str) -> list[TypedEntity]:
        """
        특정 Document의 Entity 목록 조회

        Args:
            doc_id: Document ID

        Returns:
            Entity 목록
        """
        ...

    def get_document_ids_by_entity(self, entity_name: str) -> list[str]:
        """
        특정 Entity가 언급된 Document ID 목록

        Args:
            entity_name: Entity 이름

        Returns:
            Document ID 목록 (UUID 문자열)
        """
        ...

    def list_all_entities(self, limit: int = 100) -> list[TypedEntity]:
        """
        전체 Entity 목록 조회 (type별 정렬)

        Args:
            limit: 최대 조회 개수

        Returns:
            Entity 목록
        """
        ...
