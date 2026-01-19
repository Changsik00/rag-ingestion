from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # UUID를 str로 직렬화하여 사용 (Neo4j/Chroma 호환성)
    content: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        frozen = False  # To allow mutation if needed, or keep True if we want strict immutability.
        # But previous code used frozen=True. Let's stick to Pydantic V2 ConfigDict if possible, 
        # but to minimize changes, let's keep simple class Config. 

# Backward compatibility alias
AtomicDocument = Document
