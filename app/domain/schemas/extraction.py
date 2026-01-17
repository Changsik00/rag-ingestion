
from pydantic import BaseModel, ConfigDict, Field

from app.domain.schemas.ontology import EntityType


class ExtractedMetadata(BaseModel):
    """Schema for metadata extracted from text using LLM."""

    title: str | None = Field(description="A concise and accurate title for the content.")
    summary: str = Field(description="A comprehensive summary of the content (approx. 3 sentences).")
    keywords: list[str] = Field(description="List of 5-10 key topics or tags related to the content.")
    entities: dict[EntityType, list[str]] = Field(
        description="Extracted entities grouped by standardized type (EntityType enum)."
    )

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
                    "ACTIVITY": ["벤치마킹", "프로토타이핑"]
                }
            }
        }
    )
