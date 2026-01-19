# Implementation Plan: Spec 019 - Advanced Chunking Strategy

## 📋 Branch Strategy
- `feature/019-advanced-chunking-strategy`

## 🛑 User Review Required
- [ ] **Data Migration**: 기존에 수집된 문서는 청킹되지 않은 상태입니다. 이 변경 사항 적용 시 기존 데이터는 검색 품질이 떨어지거나 호환되지 않을 수 있습니다. (현재 개발 단계이므로 DB 초기화(`RESET_DB=true`)를 권장합니다.)
- [ ] **ChromaDB Schema**: 기존에는 `Document` ID 기준이었으나, 이제는 `Chunk` ID 기준으로 임베딩이 저장됩니다.

## 🎯 Core Strategy
- **Context Preservation (Overlap)**: `RecursiveCharacterTextSplitter`의 `chunk_overlap` 기능을 활용하여 청크 간 맥락을 보존합니다. 예를 들어, 청크 1의 끝부분 200자가 청크 2의 시작부분에 포함되도록 하여 정보 단절을 막습니다.
- **LangChain Integration**: 검증된 라이브러리인 `langchain-text-splitters`를 사용하여 복잡한 로직 구현 비용을 줄이고 안정성을 확보합니다.
- **Graph + Vector Hybrid**: 논리적 구조(포함 관계)는 Neo4j 그래프로, 의미적 내용(벡터)은 ChromaDB로 분리하여 저장하되, 식별자(`chunk_id`, `parent_id`)를 통해 일관성을 유지합니다.
- **Configurable**: `CHUNK_SIZE`와 `CHUNK_OVERLAP`을 환경 변수로 관리하여 튜닝 가능하게 합니다.

## 📂 Proposed Changes

### [Core]
#### [MODIFY] `app/core/config.py`
- `CHUNK_SIZE` (default: 1000)
- `CHUNK_OVERLAP` (default: 200) 설정 추가

### [Domain]
#### [NEW] `app/domain/entities/chunk.py`
- `Chunk` dataclass 정의 (id, content, parent_id, index, metadata)
#### [NEW] `app/domain/services/chunker.py`
- `ChunkerService` 프로토콜 및 `LangChainChunker` 구현체
- `RecursiveCharacterTextSplitter` 설정 시 `chunk_overlap` 파라미터 적용

#### [MODIFY] `app/domain/entities/document.py`
- `Document` 엔티티가 `List[Chunk]`를 가질 수 있도록 확장 (Optional)

### [Infrastructure]
#### [MODIFY] `app/infrastructure/storage/neo4j_document_repository.py`
- 저장 로직 수정: `Document` 노드 생성 후 `Chunk` 노드 생성 및 `[:HAS_CHUNK]` 관계 연결
#### [MODIFY] `app/infrastructure/storage/chroma.py`
- 저장 로직 수정: `Document` 텍스트 대신 `Chunk` 리스트를 받아 벡터화 및 저장

### [Application]
#### [MODIFY] `app/use_cases/ingestion.py`
- `IngestionService`에서 `ChunkerService`를 주입받아 저장 전 분할 수행

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests
uv run pytest tests/unit/test_chunker.py
# -> test_overlap_preservation: 오버랩이 실제로 적용되었는지 문자열 비교 검증

uv run pytest tests/unit/test_ingestion_service.py

# Integration Tests
uv run pytest tests/integration/test_chunking_flow.py
```

### Manual Verification
1. `POST /ingest/web`으로 긴 아티클 수집
2. Neo4j Browser에서 `MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk) RETURN d, c` 쿼리로 구조 확인
3. **Overlap 확인**: 생성된 인접 청크(Chunk N, Chunk N+1)를 조회하여 텍스트가 겹치는지 육안 검증
