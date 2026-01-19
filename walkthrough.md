# Spec 019: Advanced Chunking Strategy Walkthrough

이 문서는 **Spec 019: Advanced Chunking Strategy** 구현에 대한 상세 설명과 검증 결과를 포함합니다.

## 구현 요약

RAG(Retrieval-Augmented Generation) 성능 향상을 위해 문서 저장 방식을 "문서 단위 저장"에서 "Chunk 단위 저장"으로 변경했습니다.

### 주요 변경 사항

1.  **Chunk Entity 정의**:
    - `Chunk` dataclass 정의 (id, content, parent_id, index, metadata).
    - `App/Domain/Entities/chunk.py`

2.  **Chunker Service 구현 (LangChain 통합)**:
    - `ChunkerService` 프로토콜 및 `LangChainChunker` 구현체 작성.
    - `RecursiveCharacterTextSplitter` 사용 (Chunk Size: 1000, Overlap: 200).
    - 설정(`app/core/config.py`)을 통한 유연한 크기 관리.

3.  **저장소(Storage) 계층 구조 변경**:
    - **Neo4j**: `Document` 노드와 `Chunk` 노드를 분리하고 `[:HAS_CHUNK]` 관계로 연결.
        - `save_with_chunks(document, chunks)` 메서드 추가.
    - **ChromaDB**: `Document` 전체 임베딩 대신 `Chunk` 단위 임베딩 저장.
        - 검색 시 `Chunk` 단위로 유사도 검색 수행 (RAG 정확도 향상).
    - **CompositeStorage**: `save_with_chunks`를 통해 Neo4j와 ChromaDB에 분산 저장 조율.

4.  **Ingestion Pipeline 업데이트**:
    - `IngestionService`에 `ChunkerService` 주입.
    - Scrape -> **Chunk** -> Save -> Graph Build 순으로 파이프라인 변경.

## 검증 결과

### 1. Unit Tests
모든 유닛 테스트가 통과했습니다.
- `tests/unit/test_chunker.py`: 텍스트 분할 및 메타데이터 보존 확인.
- `tests/unit/test_neo4j_storage.py`: Neo4j 내 Chunk 노드 및 관계 생성 쿼리 검증.
- `tests/unit/test_chroma_storage.py`: Chunk 리스트의 임베딩 저장 로직 검증.
- `tests/unit/test_ingestion_service.py`: 파이프라인 내 Chunker 호출 및 저장 로직 검증.

### 2. Integration Tests
BDD 스타일의 통합 테스트(`tests/integration/bdd/test_chunking.py`)를 통해 실제 서비스 흐름을 검증했습니다.
- 웹 페이지 수집 요청 -> Job 생성 -> Chunking -> 저장소 호출 (Spy) -> Job 완료 상태 확인.

### 3. 구조 변경 시각화 (Neo4j)
기존: `(Document)`
변경 후: `(Document) -[:HAS_CHUNK]-> (Chunk {index: 0}) -> ...`

## 사용 방법 (Developers)

```python
# IngestionService는 자동으로 Chunker를 사용합니다.
# 수동으로 Chunking을 테스트하려면:

from app.infrastructure.chunker.langchain_chunker import LangChainChunker
from app.domain.entities.document import Document

chunker = LangChainChunker()
doc = Document(content="Very long text...", metadata={})
chunks = chunker.chunk_document(doc)

print(len(chunks))
print(chunks[0].content)
```

## 향후 개선 사항
- **Google Semantic Chunking**: 현재는 Recursive Character 방식이나, 향후 의미 기반 분할 도입 예정 (Icebox).
- **Retrieval API**: 현재 `GET /documents`는 문서 목록만 반환함. Chunk 검색/조회 API (`GET /documents/{id}/chunks` or `POST /search`) 구현 필요 (별도 Spec).
