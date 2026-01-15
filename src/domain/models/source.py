import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class Chunk(BaseModel):
    """
    Source에서 분할된 텍스트 조각(Chunk)을 나타내는 엔티티.
    """
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Source(BaseModel):
    """
    수집 대상(원본 데이터)을 나타내는 엔티티.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: HttpUrl
    title: Optional[str] = None
    raw_content: Optional[str] = None
    chunks: List[Chunk] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
