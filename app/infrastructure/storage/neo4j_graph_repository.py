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
            result = session.run(
                cq.MERGE_ENTITY,
                name=name,
                type=entity_type.value
            ).single()
            return result["name"]

    def create_mention_relationship(
        self,
        doc_id: str,
        entity_name: str
    ) -> None:
        """Document-Entity MENTIONS 관계 생성"""
        with self.driver.session() as session:
            session.run(
                cq.CREATE_MENTIONS_RELATIONSHIP,
                doc_id=doc_id,
                entity_name=entity_name
            )

    def get_entities_by_document(self, doc_id: str) -> list[TypedEntity]:
        """특정 Document의 Entity 목록"""
        entities = []
        with self.driver.session() as session:
            results = session.run(cq.GET_ENTITIES_BY_DOCUMENT, doc_id=doc_id)
            for record in results:
                entities.append(TypedEntity(
                    name=record["name"],
                    type=EntityType(record["type"])
                ))
        return entities

    def get_document_ids_by_entity(self, entity_name: str) -> list[str]:
        """특정 Entity가 언급된 Document ID 목록"""
        doc_ids = []
        with self.driver.session() as session:
            results = session.run(
                cq.GET_DOCUMENT_IDS_BY_ENTITY,
                entity_name=entity_name
            )
            doc_ids = [record["doc_id"] for record in results]
        return doc_ids

    def list_all_entities(self, limit: int = 100) -> list[TypedEntity]:
        """전체 Entity 목록 (type별 정렬)"""
        entities = []
        with self.driver.session() as session:
            results = session.run(cq.LIST_ALL_ENTITIES, limit=limit)
            for record in results:
                entities.append(TypedEntity(
                    name=record["name"],
                    type=EntityType(record["type"])
                ))
        return entities
