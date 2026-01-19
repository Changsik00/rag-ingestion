"""
Graph Repository Interface (Protocol)

Domain Layer에서 Knowledge Graph 저장소의 계약을 정의합니다.
Infrastructure Layer의 구현체(Neo4jGraphRepository)는 이 Protocol을 준수해야 합니다.
"""

from typing import Any, Protocol

from app.domain.schemas.ontology import EntityType, RelationshipType, TypedEntity


class GraphRepository(Protocol):
    """
    Graph DB 저장소 인터페이스 (Protocol)

    Document-Entity 및 Entity-Entity 관계를 관리하는 저장소의 계약.
    """

    def save_entity(self, name: str, entity_type: EntityType) -> str:
        """
        Entity 노드를 Graph DB에 저장

        Args:
            name: Entity 이름
            entity_type: Entity 타입 (Enum)

        Returns:
            str: 저장된 Entity ID
        """
        ...

    def create_mention_relationship(self, document_id: str, entity_name: str) -> None:
        """
        Document -[:MENTIONS]-> Entity 관계 생성

        Args:
            document_id: 문서 ID
            entity_name: Entity 이름
        """
        ...

    def create_entity_relationship(
        self, source_name: str, relationship_type: RelationshipType, target_name: str
    ) -> None:
        """
        Entity -[relationship]-> Entity 관계 생성

        Args:
            source_name: Source entity 이름
            relationship_type: 관계 타입 (FOUNDED, WORKS_FOR 등)
            target_name: Target entity 이름
        """
        ...

    def get_entity_relationships(
        self, entity_name: str, relationship_type: RelationshipType | None = None
    ) -> list[dict[str, Any]]:
        """
        특정 Entity의 모든 관계 조회

        Args:
            entity_name: 조회할 Entity 이름
            relationship_type: 필터링할 관계 타입 (Optional)

        Returns:
            List[Dict]: 관계 목록
            [
                {
                    "relationship_type": "FOUNDED",
                    "target_name": "Tesla",
                    "target_type": "ORGANIZATION"
                }
            ]
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
