from typing import List, TypedDict
from src.domain.models.source import Source

class GraphState(TypedDict):
    urls: List[str]
    sources: List[Source]
    errors: List[str]
    status: str
