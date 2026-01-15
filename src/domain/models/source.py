from typing import List, Dict, Any, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl

class Chunk(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Source(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: HttpUrl
    title: Optional[str] = None
    raw_content: Optional[str] = None
    chunks: List[Chunk] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
