"""
Unit Tests for Neo4jGraphRepository

Neo4jGraphRepository의 각 메서드를 독립적으로 테스트합니다.
Mock Neo4j driver를 사용하여 실제 DB 없이 테스트합니다.
"""

from unittest.mock import MagicMock, Mock

import pytest

from app.domain.value_objects.ontology import EntityType, RelationshipType, TypedEntity
from app.infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository


@pytest.fixture
def mock_driver():
    """Mock Neo4j Driver"""
    driver = Mock()
    session = MagicMock()

    # Context manager 설정
    driver.session.return_value = MagicMock()
    driver.session.return_value.__enter__.return_value = session
    driver.session.return_value.__exit__.return_value = None

    return driver, session


def test_save_entity_creates_node(mock_driver):
    """Entity 노드 생성 검증"""
    # Given: Mock driver와 session
    driver, session = mock_driver

    # Mock result
    mock_result = Mock()
    mock_result.single.return_value = {"name": "Elon Musk"}
    session.run.return_value = mock_result

    # When: Entity 저장
    repo = Neo4jGraphRepository(driver)
    result = repo.save_entity("Elon Musk", EntityType.PERSON)

    # Then: Entity가 생성됨
    assert result == "Elon Musk"
    assert session.run.call_count >= 1  # CREATE_ENTITY_INDEX + MERGE_ENTITY


def test_save_entity_merge_duplicates(mock_driver):
    """중복 Entity MERGE 검증 - 같은 이름은 하나만 생성"""
    # Given: Mock driver와 repository
    driver, session = mock_driver

    mock_result = Mock()
    mock_result.single.return_value = {"name": "Tesla"}
    session.run.return_value = mock_result

    repo = Neo4jGraphRepository(driver)

    # When: 동일한 Entity를 두 번 저장
    result1 = repo.save_entity("Tesla", EntityType.TECHNOLOGY)
    result2 = repo.save_entity("Tesla", EntityType.TECHNOLOGY)

    # Then: 두 결과 모두 동일한 Entity 이름 반환 (MERGE됨)
    assert result1 == "Tesla"
    assert result2 == "Tesla"


def test_create_mention_relationship(mock_driver):
    """MENTIONS 관계 생성 검증"""
    # Given: Repository와 document ID, entity name
    driver, session = mock_driver
    repo = Neo4jGraphRepository(driver)

    # When: MENTIONS 관계 생성
    repo.create_mention_relationship("doc-123", "Elon Musk")

    # Then: 쿼리가 실행됨
    assert session.run.call_count >= 1  # CREATE_ENTITY_INDEX + MENTIONS


def test_get_entities_by_document(mock_driver):
    """Document 기반 Entity 조회"""
    # Given: Document와 연결된 Entities Mock
    driver, session = mock_driver

    mock_records = [{"name": "Elon Musk", "type": "PERSON"}, {"name": "Tesla", "type": "TECHNOLOGY"}]
    session.run.return_value = mock_records

    # When: Document ID로 Entity 조회
    repo = Neo4jGraphRepository(driver)
    entities = repo.get_entities_by_document("doc-123")

    # Then: TypedEntity 리스트 반환
    assert len(entities) == 2
    assert isinstance(entities[0], TypedEntity)
    assert entities[0].name == "Elon Musk"
    assert entities[0].type == EntityType.PERSON
    assert entities[1].name == "Tesla"
    assert entities[1].type == EntityType.TECHNOLOGY


def test_get_document_ids_by_entity(mock_driver):
    """Entity 기반 Document 조회"""
    # Given: Entity와 연결된 Documents Mock
    driver, session = mock_driver

    mock_records = [{"doc_id": "doc-1"}, {"doc_id": "doc-2"}, {"doc_id": "doc-3"}]
    session.run.return_value = mock_records

    # When: Entity 이름으로 Document 조회
    repo = Neo4jGraphRepository(driver)
    doc_ids = repo.get_document_ids_by_entity("Elon Musk")

    # Then: Document ID 리스트 반환
    assert len(doc_ids) == 3
    assert "doc-1" in doc_ids
    assert "doc-2" in doc_ids
    assert "doc-3" in doc_ids


def test_list_all_entities(mock_driver):
    """전체 Entity 목록 조회"""
    # Given: 전체 Entities Mock
    driver, session = mock_driver

    mock_records = [
        {"name": "Elon Musk", "type": "PERSON"},
        {"name": "Tesla", "type": "TECHNOLOGY"},
        {"name": "OpenAI", "type": "ORGANIZATION"},
    ]
    session.run.return_value = mock_records

    # When: 전체 Entity 리스트 조회 (limit=100)
    repo = Neo4jGraphRepository(driver)
    entities = repo.list_all_entities(limit=100)

    # Then: TypedEntity 리스트 반환
    assert len(entities) == 3
    assert all(isinstance(e, TypedEntity) for e in entities)
    assert entities[0].name == "Elon Musk"


def test_list_all_entities_respects_limit(mock_driver):
    """limit 파라미터가 쿼리에 전달되는지 확인"""
    # Given: Mock driver와 repository
    driver, session = mock_driver
    session.run.return_value = []

    # When: limit=50으로 Entity 조회
    repo = Neo4jGraphRepository(driver)
    repo.list_all_entities(limit=50)

    # Then: limit 파라미터가 쿼리에 전달됨
    last_call_args = session.run.call_args
    assert last_call_args is not None
    if len(last_call_args) > 1:
        assert last_call_args[1].get("limit") == 50 or last_call_args.kwargs.get("limit") == 50


# ===== Task 9-2: Relationship Method Tests =====


def test_create_entity_relationship(mock_driver):
    """Entity-Entity 관계 생성 테스트"""
    # Given: Mock driver와 relationship 정보
    driver, session = mock_driver

    mock_result = Mock()
    mock_result.single.return_value = {"relationship_type": "FOUNDED"}
    session.run.return_value = mock_result

    # When: Entity 관계 생성
    repo = Neo4jGraphRepository(driver)
    repo.create_entity_relationship(
        source_name="Elon Musk", relationship_type=RelationshipType.FOUNDED, target_name="Tesla"
    )

    # Then: Cypher 쿼리가 실행됨
    assert session.run.called
    call_args = session.run.call_args
    # Query에 FOUNDED가 포함되어야 함 (동적 쿼리 생성)
    query_str = str(call_args[0][0])
    assert "FOUNDED" in query_str


def test_get_entity_relationships_all(mock_driver):
    """Entity의 모든 관계 조회 테스트"""
    # Given: Mock relationships
    driver, session = mock_driver

    mock_records = [
        {"relationship_type": "FOUNDED", "target_name": "Tesla", "target_type": "ORGANIZATION"},
        {"relationship_type": "FOUNDED", "target_name": "SpaceX", "target_type": "ORGANIZATION"},
    ]
    session.run.return_value = mock_records

    # When: 모든 관계 조회 (type 필터 없음)
    repo = Neo4jGraphRepository(driver)
    relationships = repo.get_entity_relationships("Elon Musk")

    # Then: 관계 리스트 반환
    assert len(relationships) == 2
    assert relationships[0]["relationship_type"] == "FOUNDED"
    assert relationships[0]["target_name"] == "Tesla"
    assert relationships[1]["target_name"] == "SpaceX"


def test_get_entity_relationships_filtered(mock_driver):
    """특정 타입의 관계만 조회 테스트"""
    # Given: Mock filtered relationships
    driver, session = mock_driver

    mock_records = [{"relationship_type": "USES", "target_name": "Python", "target_type": "TECHNOLOGY"}]
    session.run.return_value = mock_records

    # When: USES 타입만 필터링
    repo = Neo4jGraphRepository(driver)
    relationships = repo.get_entity_relationships("Tesla", relationship_type=RelationshipType.USES)

    # Then: USES 관계만 반환
    assert len(relationships) == 1
    assert relationships[0]["relationship_type"] == "USES"
    assert session.run.called
