from typing import Protocol, List

from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document


class ChunkerService(Protocol):
    """문서를 청크로 분할하는 도메인 서비스 인터페이스"""

    def chunk_document(self, document: Document) -> List[Chunk]:
        """하나의 문서를 여러 개의 청크로 분할한다."""
        ...
