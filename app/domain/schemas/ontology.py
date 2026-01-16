"""
Domain Layer - Ontology Schema

Entity 타입과 Relationship 타입을 정의하는 스키마.
향후 Knowledge Graph 구축의 기반이 되는 데이터 계약(Data Contract).
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """
    표준화된 Entity 타입 분류
    
    LLM이 추출한 Entity를 7가지 타입으로 분류.
    자유 형식 문자열 대신 Enum을 사용하여 타입 안정성 확보.
    """
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    TECHNOLOGY = "TECHNOLOGY"
    CONCEPT = "CONCEPT"
    LOCATION = "LOCATION"
    EVENT = "EVENT"
    ACTIVITY = "ACTIVITY"


class RelationshipType(str, Enum):
    """
    Entity 간 관계 타입 (향후 Spec 008에서 활용)
    
    현재는 스키마 정의만 수행하고, 실제 관계 추출 및 
    Neo4j 저장은 Spec 008에서 구현 예정.
    """
    # Document-Entity 관계
    MENTIONS = "MENTIONS"              # Document -> Entity
    
    # Person 관계
    WORKS_FOR = "WORKS_FOR"            # Person -> Organization
    FOUNDED = "FOUNDED"                # Person -> Organization
    PERFORMED = "PERFORMED"            # Person -> Activity
    
    # Technology/Concept 관계
    USES = "USES"                      # Organization -> Technology
    SUPPORTS = "SUPPORTS"              # Technology -> Activity
    RELATED_TO = "RELATED_TO"          # Concept -> Concept
    
    # Activity 관계
    PART_OF = "PART_OF"                # Activity -> Activity


class TypedEntity(BaseModel):
    """
    Entity 분류 결과 (향후 확장용)
    
    현재는 사용하지 않지만, 향후 Entity에 신뢰도(confidence) 등
    추가 메타데이터를 붙일 때 활용 가능.
    
    Example:
        >>> entity = TypedEntity(
        ...     name="Elon Musk",
        ...     type=EntityType.PERSON,
        ...     confidence=0.95
        ... )
    """
    name: str = Field(description="Entity 이름")
    type: EntityType = Field(description="Entity 타입")
    confidence: float = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0,
        description="분류 신뢰도 (0.0 ~ 1.0)"
    )
