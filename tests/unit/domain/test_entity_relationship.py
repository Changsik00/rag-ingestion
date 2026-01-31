"""
Unit Tests for EntityRelationship Schema

Task 9-1: Domain Schema Tests
"""

import pytest
from pydantic import ValidationError

from app.domain.value_objects.extracted_metadata import EntityRelationship
from app.domain.value_objects.ontology import EntityType, RelationshipType


def test_entity_relationship_creation():
    """EntityRelationship 정상 생성 테스트"""
    rel = EntityRelationship(
        source="Elon Musk",
        source_type=EntityType.PERSON,
        relationship=RelationshipType.FOUNDED,
        target="Tesla",
        target_type=EntityType.ORGANIZATION,
    )

    assert rel.source == "Elon Musk"
    assert rel.source_type == EntityType.PERSON
    assert rel.relationship == RelationshipType.FOUNDED
    assert rel.target == "Tesla"
    assert rel.target_type == EntityType.ORGANIZATION
    assert rel.confidence == 1.0  # default


def test_entity_relationship_with_confidence():
    """Confidence 값 포함 생성 테스트"""
    rel = EntityRelationship(
        source="Jane",
        source_type=EntityType.PERSON,
        relationship=RelationshipType.WORKS_FOR,
        target="Google",
        target_type=EntityType.ORGANIZATION,
        confidence=0.85,
    )

    assert rel.confidence == 0.85


def test_confidence_range_validation():
    """Confidence 범위 검증 (0.0 ~ 1.0)"""
    # Valid: 0.0
    rel1 = EntityRelationship(
        source="A",
        source_type=EntityType.PERSON,
        relationship=RelationshipType.FOUNDED,
        target="B",
        target_type=EntityType.ORGANIZATION,
        confidence=0.0,
    )
    assert rel1.confidence == 0.0

    # Valid: 1.0
    rel2 = EntityRelationship(
        source="A",
        source_type=EntityType.PERSON,
        relationship=RelationshipType.FOUNDED,
        target="B",
        target_type=EntityType.ORGANIZATION,
        confidence=1.0,
    )
    assert rel2.confidence == 1.0

    # Invalid: > 1.0
    with pytest.raises(ValidationError) as exc_info:
        EntityRelationship(
            source="A",
            source_type=EntityType.PERSON,
            relationship=RelationshipType.FOUNDED,
            target="B",
            target_type=EntityType.ORGANIZATION,
            confidence=1.5,
        )
    assert "less than or equal to 1" in str(exc_info.value)

    # Invalid: < 0.0
    with pytest.raises(ValidationError) as exc_info:
        EntityRelationship(
            source="A",
            source_type=EntityType.PERSON,
            relationship=RelationshipType.FOUNDED,
            target="B",
            target_type=EntityType.ORGANIZATION,
            confidence=-0.1,
        )
    assert "greater than or equal to 0" in str(exc_info.value)


def test_all_relationship_types():
    """모든 RelationshipType 사용 가능 확인"""
    relationship_types = [
        RelationshipType.FOUNDED,
        RelationshipType.WORKS_FOR,
        RelationshipType.USES,
        RelationshipType.RELATED_TO,
        RelationshipType.SUPPORTS,
        RelationshipType.PERFORMED,
        RelationshipType.PART_OF,
    ]

    for rel_type in relationship_types:
        rel = EntityRelationship(
            source="Source",
            source_type=EntityType.PERSON,
            relationship=rel_type,
            target="Target",
            target_type=EntityType.ORGANIZATION,
        )
        assert rel.relationship == rel_type


def test_entity_relationship_serialization():
    """EntityRelationship JSON 직렬화 테스트"""
    rel = EntityRelationship(
        source="Netflix",
        source_type=EntityType.ORGANIZATION,
        relationship=RelationshipType.USES,
        target="Python",
        target_type=EntityType.TECHNOLOGY,
        confidence=0.95,
    )

    data = rel.model_dump()

    assert data["source"] == "Netflix"
    assert data["source_type"] == "ORGANIZATION"
    assert data["relationship"] == "USES"
    assert data["target"] == "Python"
    assert data["target_type"] == "TECHNOLOGY"
    assert data["confidence"] == 0.95
