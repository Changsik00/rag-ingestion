from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AtomicDocument(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    content: str
    source_url: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        frozen = True # Entities should be treated carefully, but Pydantic's frozen makes it immutable-ish which is good for safety.
