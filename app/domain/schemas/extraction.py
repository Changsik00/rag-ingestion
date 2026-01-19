from pydantic import BaseModel, ConfigDict, Field

from app.domain.schemas.ontology import EntityType, RelationshipType


class EntityRelationship(BaseModel):
    """
    LLM이 추출한 Entity 간 관계

    Example:
        >>> rel = EntityRelationship(
        ...     source="Elon Musk",
        ...     source_type=EntityType.PERSON,
        ...     relationship=RelationshipType.FOUNDED,
        ...     target="Tesla",
        ...     target_type=EntityType.ORGANIZATION
        ... )
    """

    source: str = Field(description="Source entity name")
    source_type: EntityType = Field(description="Source entity type")
    relationship: RelationshipType = Field(description="Relationship type")
    target: str = Field(description="Target entity name")
    target_type: EntityType = Field(description="Target entity type")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="관계 추출 신뢰도 (0.0 ~ 1.0)")


class ExtractedMetadata(BaseModel):
    """Schema for metadata extracted from text using LLM."""

    title: str | None = Field(description="A concise and accurate title for the content.")
    summary: str = Field(description="A comprehensive summary of the content (approx. 3 sentences).")
    keywords: list[str] = Field(description="List of 5-10 key topics or tags related to the content.")
    entities: dict[EntityType, list[str]] = Field(default_factory=dict, description="분류된 Entity 목록 (타입별)")
    relationships: list[EntityRelationship] = Field(default_factory=list, description="Entity 간 관계 목록")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Introduction to Vector Databases",
                "summary": "This article explains the concept of vector databases and their importance in AI applications. It covers how embeddings work and compares different indexing algorithms like HNSW.",
                "keywords": ["Vector Database", "Embeddings", "AI", "HNSW", "Search"],
                "entities": {
                    "TECHNOLOGY": ["ChromaDB", "Pinecone", "Python"],
                    "CONCEPT": ["High-dimensional space", "Cosine Similarity"],
                    "PERSON": ["Geoffrey Hinton"],
                    "ACTIVITY": ["벤치마킹", "프로토타이핑"],
                },
            }
        }
    )
