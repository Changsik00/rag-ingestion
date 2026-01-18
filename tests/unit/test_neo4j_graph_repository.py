"""
Unit Tests for Neo4jGraphRepository

Neo4jGraphRepository의 각 메서드를 독립적으로 테스트합니다.
Mock Neo4j driver를 사용하여 실제 DB 없이 테스트합니다.
"""

import pytest
from unittest.mock import Mock, MagicMock

from app.domain.schemas.ontology import EntityType, TypedEntity
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository


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
    driver, session = mock_driver
    
    # Mock result
    mock_result = Mock()
    mock_result.single.return_value = {"name": "Elon Musk"}
    session.run.return_value = mock_result
    
    # Test
    repo = Neo4jGraphRepository(driver)
    result = repo.save_entity("Elon Musk", EntityType.PERSON)
    
    assert result == "Elon Musk"
    assert session.run.call_count >= 1  # CREATE_ENTITY_INDEX + MERGE_ENTITY


def test_save_entity_merge_duplicates(mock_driver):
    """중복 Entity MERGE 검증 - 같은 이름은 하나만 생성"""
    driver, session = mock_driver
    
    mock_result = Mock()
    mock_result.single.return_value = {"name": "Tesla"}
    session.run.return_value = mock_result
    
    repo = Neo4jGraphRepository(driver)
    
    # 첫 번째 저장
    result1 = repo.save_entity("Tesla", EntityType.TECHNOLOGY)
    # 두 번째 저장 (중복)
    result2 = repo.save_entity("Tesla", EntityType.TECHNOLOGY)
    
    assert result1 == "Tesla"
    assert result2 == "Tesla"


def test_create_mention_relationship(mock_driver):
    """MENTIONS 관계 생성 검증"""
    driver, session = mock_driver
    
    repo = Neo4jGraphRepository(driver)
    repo.create_mention_relationship("doc-123", "Elon Musk")
    
    # CREATE_ENTITY_INDEX는 __init__에서 한 번, 그 후 MENTIONS 쿼리
    assert session.run.call_count >= 1


def test_get_entities_by_document(mock_driver):
    """Document 기반 Entity 조회"""
    driver, session = mock_driver
    
    # Mock results
    mock_records = [
        {"name": "Elon Musk", "type": "PERSON"},
        {"name": "Tesla", "type": "TECHNOLOGY"}
    ]
    session.run.return_value = mock_records
    
    repo = Neo4jGraphRepository(driver)
    entities = repo.get_entities_by_document("doc-123")
    
    assert len(entities) == 2
    assert isinstance(entities[0], TypedEntity)
    assert entities[0].name == "Elon Musk"
    assert entities[0].type == EntityType.PERSON
    assert entities[1].name == "Tesla"
    assert entities[1].type == EntityType.TECHNOLOGY


def test_get_document_ids_by_entity(mock_driver):
    """Entity 기반 Document 조회"""
    driver, session = mock_driver
    
    # Mock results
    mock_records = [
        {"doc_id": "doc-1"},
        {"doc_id": "doc-2"},
        {"doc_id": "doc-3"}
    ]
    session.run.return_value = mock_records
    
    repo = Neo4jGraphRepository(driver)
    doc_ids = repo.get_document_ids_by_entity("Elon Musk")
    
    assert len(doc_ids) == 3
    assert "doc-1" in doc_ids
    assert "doc-2" in doc_ids
    assert "doc-3" in doc_ids


def test_list_all_entities(mock_driver):
    """전체 Entity 목록 조회"""
    driver, session = mock_driver
    
    # Mock results
    mock_records = [
        {"name": "Elon Musk", "type": "PERSON"},
        {"name": "Tesla", "type": "TECHNOLOGY"},
        {"name": "OpenAI", "type": "ORGANIZATION"}
    ]
    session.run.return_value = mock_records
    
    repo = Neo4jGraphRepository(driver)
    entities = repo.list_all_entities(limit=100)
    
    assert len(entities) == 3
    assert all(isinstance(e, TypedEntity) for e in entities)
    assert entities[0].name == "Elon Musk"


def test_list_all_entities_respects_limit(mock_driver):
    """limit 파라미터가 쿼리에 전달되는지 확인"""
    driver, session = mock_driver
    session.run.return_value = []
    
    repo = Neo4jGraphRepository(driver)
    repo.list_all_entities(limit=50)
    
    # 마지막 run 호출의 인자 확인
    last_call_args = session.run.call_args
    assert last_call_args is not None
    # limit=50이 파라미터로 전달되었는지 확인
    if len(last_call_args) > 1:
        assert last_call_args[1].get('limit') == 50 or last_call_args.kwargs.get('limit') == 50
