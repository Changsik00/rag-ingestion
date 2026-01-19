# Task List: Spec 019 - Advanced Chunking Strategy

## Progress

- [ ] Spec 번호 확정 (019)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Spec 018 완료 처리 포함)
- [ ] User Plan Accept

---

## Task 1: Setup & Configuration

### 1-1. Branch & Housekeeping
- [x] 브랜치 생성: `git checkout -b feature/019-advanced-chunking-strategy`
- [x] 백로그 업데이트: `backlog/queue.md` (Spec 018 [x], Spec 019 [/])
- [x] Commit: `chore(spec-019): start spec 019 and update backlog`

### 1-2. Configuration
- [x] 코드 구현: `app/core/config.py` 생성 및 설정 클래스(Pydantic BaseSettings) 구현
    - `CHUNK_SIZE` (default: 1000)
    - `CHUNK_OVERLAP` (default: 200)
- [x] Commit: `feat(spec-019): add centralized settings with pydantic`

### 1-3. Documentation Update
- [x] 문서 작성: `docs/llm_strategy.md` (Embedding 및 Chunking 전략 기술)
- [x] Commit: `docs(spec-019): add llm strategy guide with chunking details`

---

## Task 2: Domain Layer (Chunking Logic)

### 2-1. Chunk Entity & Interface
- [x] 코드 구현: `app/domain/entities/chunk.py` (Data Structure)
- [x] 코드 구현: `app/domain/services/chunker.py` (Protocol Definition)
- [x] Commit: `feat(spec-019): define chunk entity and service interface`

### 2-2. Chunker Implementation (TDD)
- [x] Test Case 작성: `tests/unit/test_chunker.py` (Recursive splitting 동작 검증)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/test_chunker.py`
- [x] 코드 구현: `app/domain/services/chunker.py` (DefaultChunker 구현 w/ LangChain)
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_chunker.py`
- [x] Commit: `feat(spec-019): implement langchain-based chunker service`

---

## Task 3: Infrastructure Layer (Storage)

### 3-1. Neo4j Chunk Storage (TDD)
- [x] Test Case 수정: `tests/unit/test_neo4j_storage.py` (Chunk 저장 및 관계 생성 검증)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/test_neo4j_storage.py`
- [x] 코드 수정: `app/infrastructure/storage/neo4j_document_repository.py`
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_neo4j_storage.py`
- [x] Commit: `refactor(spec-019): update neo4j repository to store chunks`

### 3-2. ChromaDB Chunk Storage (TDD)
- [x] Test Case 수정: `tests/unit/test_chroma_storage.py` (Chunk 리스트 처리 검증)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/test_chroma_storage.py`
- [x] 코드 수정: `app/infrastructure/storage/chroma.py`
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_chroma_storage.py`
- [x] Commit: `refactor(spec-019): update chroma storage to handle chunk embeddings`

### 3-3. Composite Storage & Interface Update
- [x] 코드 수정: `app/domain/interfaces/document_repository.py` (save_with_chunks 추가)
- [x] 코드 수정: `app/infrastructure/storage/composite.py` (Chunk 저장 위임 구현)
- [x] Test 추가: `tests/unit/test_storage.py` (Composite Chunk 저장 검증)
- [x] Commit: `refactor(spec-019): update repository interface and composite storage for chunking`

---

## Task 4: Application Layer Integration

### 4-1. Ingestion Pipeine Update (TDD)
- [x] Test Case 수정: `tests/unit/test_ingestion_service.py` (Chunker 호출 여부 검증)
- [x] 코드 수정: `app/use_cases/ingestion.py` (Chunker 주입 및 실행 로직 추가)
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_ingestion_service.py`
- [x] Commit: `feat(spec-019): integrate chunking into ingestion pipeline`

---

## Task 5: Final Verification & PR

### 5-1. Integration Testing
- [x] Test Case 작성: `tests/integration/bdd/test_chunking.py` (End-to-End 수집 및 구조 검증)
- [x] Test 실행 (Pass): `uv run pytest tests/integration/bdd/test_chunking.py`
- [x] Commit: `test(spec-019): add bdd tests for chunking flow`

### 5-2. PR Creation
- [ ] PR 생성: `gh pr create ...` (User Action Required)
- [x] 문서 보관: `pr_description.md`, `walkthrough.md` 업데이트

## Summary
**총 Task**: 5개
**예상 커밋 수**: 8~10개
