from pydantic import BaseModel

from app.domain.value_objects.ontology import EntityType, RelationshipType


class EntityMentionResponse(BaseModel):
    name: str
    type: EntityType
    confidence: float


class EntityInfoResponse(BaseModel):
    name: str
    mention_count: int
    document_ids: list[str]


class RelationshipMentionResponse(BaseModel):
    relationship_type: RelationshipType
    target_name: str
    target_type: str
