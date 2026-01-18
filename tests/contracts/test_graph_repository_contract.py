"""
Contract Tests for GraphRepository Protocol

GraphRepository 인터페이스가 제대로 정의되었는지,
그리고 Neo4jGraphRepository가 이 계약을 준수하는지 검증합니다.
"""

import pytest
from typing import get_type_hints

from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.schemas.ontology import EntityType, TypedEntity
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository


@pytest.fixture(params=[GraphRepository, Neo4jGraphRepository])
def graph_repository_class(request):
    """GraphRepository 프로토콜과 구현체를 번갈아 가며 테스트하기 위한 픽스처"""
    return request.param


def test_graph_repository_protocol_exists():
    """GraphRepository Protocol이 정의되어 있는지 확인"""
    assert GraphRepository is not None


def test_graph_repository_has_required_methods():
    """GraphRepository가 필수 메서드를 정의하는지 확인"""
    required_methods = {
        'save_entity',
        'create_mention_relationship',
        'get_entities_by_document',
        'get_document_ids_by_entity',
        'list_all_entities'
    }
    
    protocol_methods = {
        name for name in dir(GraphRepository)
        if not name.startswith('_')
    }
    
    assert required_methods.issubset(protocol_methods), \
        f"Missing methods: {required_methods - protocol_methods}"


def test_save_entity_signature():
    """save_entity 메서드 시그니처 검증"""
    hints = get_type_hints(GraphRepository.save_entity)
    
    assert 'name' in hints
    assert 'entity_type' in hints
    assert hints['entity_type'] == EntityType
    assert hints['return'] == str


def test_get_entities_by_document_signature():
    """get_entities_by_document 메서드 시그니처 검증"""
    hints = get_type_hints(GraphRepository.get_entities_by_document)
    
    assert 'doc_id' in hints
    assert hints['doc_id'] == str
    assert hints['return'] == list[TypedEntity]


def test_neo4j_graph_repository_implements_protocol():
    """Neo4jGraphRepository가 GraphRepository Protocol을 준수하는지 확인"""
    required_methods = {
        'save_entity',
        'create_mention_relationship',
        'get_entities_by_document',
        'get_document_ids_by_entity',
        'list_all_entities'
    }
    
    impl_methods = {
        name for name in dir(Neo4jGraphRepository)
        if not name.startswith('_') and callable(getattr(Neo4jGraphRepository, name))
    }
    
    assert required_methods.issubset(impl_methods), \
        f"Neo4jGraphRepository missing methods: {required_methods - impl_methods}"


def test_neo4j_graph_repository_method_signatures():
    """Neo4jGraphRepository의 메서드 시그니처가 Protocol과 일치하는지 확인"""
    # save_entity
    impl_hints = get_type_hints(Neo4jGraphRepository.save_entity)
    protocol_hints = get_type_hints(GraphRepository.save_entity)
    
    assert impl_hints['name'] == protocol_hints['name']
    assert impl_hints['entity_type'] == protocol_hints['entity_type']
    assert impl_hints['return'] == protocol_hints['return']
    
    # get_entities_by_document
    impl_hints = get_type_hints(Neo4jGraphRepository.get_entities_by_document)
    protocol_hints = get_type_hints(GraphRepository.get_entities_by_document)
    
    assert impl_hints['doc_id'] == protocol_hints['doc_id']
    assert impl_hints['return'] == protocol_hints['return']
