import pytest
from app.domain.schemas.ontology import EntityType, RelationshipType
from app.domain.schemas.extraction import ExtractedMetadata


def test_entity_type_enum_values():
    """EntityType Enum이 7개 타입을 포함하는지 검증"""
    assert len(EntityType) == 7
    assert EntityType.PERSON.value == "PERSON"
    assert EntityType.ORGANIZATION.value == "ORGANIZATION"
    assert EntityType.TECHNOLOGY.value == "TECHNOLOGY"
    assert EntityType.CONCEPT.value == "CONCEPT"
    assert EntityType.LOCATION.value == "LOCATION"
    assert EntityType.EVENT.value == "EVENT"
    assert EntityType.ACTIVITY.value == "ACTIVITY"


def test_relationship_type_enum_values():
    """RelationshipType Enum이 8개 타입을 포함하는지 검증"""
    assert len(RelationshipType) == 8
    assert RelationshipType.MENTIONS.value == "MENTIONS"
    assert RelationshipType.WORKS_FOR.value == "WORKS_FOR"
    assert RelationshipType.FOUNDED.value == "FOUNDED"
    assert RelationshipType.USES.value == "USES"
    assert RelationshipType.RELATED_TO.value == "RELATED_TO"
    assert RelationshipType.PERFORMED.value == "PERFORMED"
    assert RelationshipType.SUPPORTS.value == "SUPPORTS"
    assert RelationshipType.PART_OF.value == "PART_OF"


def test_extracted_metadata_with_diverse_entities():
    """다양한 Entity 타입을 포함한 ExtractedMetadata 검증"""
    metadata = ExtractedMetadata(
        title="Startup Growth Strategy",
        summary="Analysis of startup scaling methods",
        keywords=["startup", "growth", "strategy"],
        entities={
            EntityType.PERSON: ["Eric Ries", "Steve Blank"],
            EntityType.ORGANIZATION: ["Y Combinator", "500 Startups"],
            EntityType.TECHNOLOGY: ["AWS", "React", "PostgreSQL"],
            EntityType.CONCEPT: ["Lean Startup", "Product-Market Fit"],
            EntityType.LOCATION: ["San Francisco", "Seoul"],
            EntityType.EVENT: ["TechCrunch Disrupt 2024"],
            EntityType.ACTIVITY: ["고객 인터뷰", "MVP 개발", "피벗팅"]
        }
    )
    assert EntityType.ACTIVITY in metadata.entities
    assert "고객 인터뷰" in metadata.entities[EntityType.ACTIVITY]
    assert len(metadata.entities) == 7  # 모든 타입 포함


def test_extracted_metadata_with_korean_activities():
    """한글 활동명이 올바르게 처리되는지 검증"""
    metadata = ExtractedMetadata(
        title="소프트웨어 개발 프로세스",
        summary="현대적인 개발 방법론",
        keywords=["개발", "프로세스"],
        entities={
            EntityType.ACTIVITY: [
                "책 쓰기", "벤치마킹", "코드 리뷰",
                "페어 프로그래밍", "회고", "스프린트 계획"
            ]
        }
    )
    assert len(metadata.entities[EntityType.ACTIVITY]) == 6
    assert "책 쓰기" in metadata.entities[EntityType.ACTIVITY]


def test_entity_type_string_enum():
    """EntityType이 str 기반 Enum인지 검증 (JSON 직렬화 용이)"""
    assert isinstance(EntityType.PERSON, str)
    assert EntityType.TECHNOLOGY == "TECHNOLOGY"


def test_relationship_type_string_enum():
    """RelationshipType이 str 기반 Enum인지 검증"""
    assert isinstance(RelationshipType.MENTIONS, str)
    assert RelationshipType.PERFORMED == "PERFORMED"
