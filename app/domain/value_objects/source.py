
from pydantic import BaseModel, HttpUrl


class Source(BaseModel):
    url: HttpUrl
    title: str | None = None

    class Config:
        frozen = True # Value Objects must be immutable
