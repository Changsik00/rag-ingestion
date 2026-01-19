from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Chunk:
    """문서의 의미론적 분할 단위 (Semantic Unit)"""
    id: str
    content: str
    parent_id: str  # 원본 Document ID
    index: int      # 문서 내 순서 (0-based)
    metadata: Dict[str, Any] = field(default_factory=dict)
