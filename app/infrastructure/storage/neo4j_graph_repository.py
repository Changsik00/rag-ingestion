"""
Neo4j 기반 Knowledge Graph 저장소 구현
"""

from neo4j import Driver

from app.domain.schemas.ontology import EntityType, TypedEntity
from app.infrastructure.storage import cypher_queries as cq


class Neo4jGraphRepository:
    """Neo4j 기반 Knowledge Graph 저장소"""

    def __init__(self, driver: Driver):
        self.driver = driver
        self._create_indexes()

    def _create_indexes(self):
        """Entity 검색 성능을 위한 인덱스 생성"""
        with self.driver.session() as session:
            session.run(cq.CREATE_ENTITY_INDEX)

    def save_entity(self, name: str, entity_type: EntityType) -> str:
        """Entity 노드 MERGE (중복 시 기존 반환)"""
        with self.driver.session() as session:
            result = session.run(cq.MERGE_ENTITY, name=name, type=entity_type.value).single()
            return result["name"]

    def create_mention_relationship(self, doc_id: str, entity_name: str) -> None:
        """Document-Entity MENTIONS 관계 생성"""
        with self.driver.session() as session:
            session.run(cq.CREATE_MENTIONS_RELATIONSHIP, doc_id=doc_id, entity_name=entity_name)

    def get_entities_by_document(self, doc_id: str) -> list[TypedEntity]:
        """특정 Document의 Entity 목록"""
        entities = []
        with self.driver.session() as session:
            results = session.run(cq.GET_ENTITIES_BY_DOCUMENT, doc_id=doc_id)
            for record in results:
                entities.append(TypedEntity(name=record["name"], type=EntityType(record["type"])))
        return entities

    def get_document_ids_by_entity(self, entity_name: str) -> list[str]:
        """특정 Entity가 언급된 Document ID 목록"""
        doc_ids = []
        with self.driver.session() as session:
            results = session.run(cq.GET_DOCUMENT_IDS_BY_ENTITY, entity_name=entity_name)
            doc_ids = [record["doc_id"] for record in results]
        return doc_ids

    def list_all_entities(self, limit: int = 100) -> list[TypedEntity]:
        """전체 Entity 목록 (type별 정렬)"""
        entities = []
        with self.driver.session() as session:
            results = session.run(cq.LIST_ALL_ENTITIES, limit=limit)
            for record in results:
                entities.append(TypedEntity(name=record["name"], type=EntityType(record["type"])))
        return entities

    def create_entity_relationship(
        self,
        source_name: str,
        relationship_type,  # RelationshipType from ontology
        target_name: str,
    ) -> None:
        """Entity-Entity 관계 생성"""
        # Cypher에서 relationship type은 동적으로 삽입해야 함
        query = cq.CREATE_ENTITY_RELATIONSHIP.replace("{relationship_type}", relationship_type.value)

        with self.driver.session() as session:
            session.run(query, source_name=source_name, target_name=target_name)

    def get_entity_relationships(
        self,
        entity_name: str,
        relationship_type=None,  # Optional[RelationshipType]
    ) -> list[dict]:
        """특정 Entity의 관계 목록 조회"""
        relationships = []

        with self.driver.session() as session:
            if relationship_type:
                # 특정 관계 타입만 필터링
                query = cq.GET_ENTITY_RELATIONSHIPS_BY_TYPE.replace("{relationship_type}", relationship_type.value)
                results = session.run(query, entity_name=entity_name)
            else:
                # 모든 관계 조회
                results = session.run(cq.GET_ENTITY_RELATIONSHIPS, entity_name=entity_name)

            for record in results:
                relationships.append(
                    {
                        "relationship_type": record["relationship_type"],
                        "target_name": record["target_name"],
                        "target_type": record["target_type"],
                    }
                )

        return relationships
