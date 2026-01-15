from pydantic import BaseModel, HttpUrl
from typing import Optional

class Source(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    
    class Config:
        frozen = True # Value Objects must be immutable
