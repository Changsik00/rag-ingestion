# Task List: Spec-056 (Semantic Chunking Upgrade)

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Core Domain & Infrastructure Implementation
### 1-1. Domain Model 확장
- [x] `ChunkingConfig` Value Object 정의: `app/domain/value_objects/chunk_config.py`
- [x] `IngestionJob` 엔티티 필드 추가 및 마이그레이션 확인: `app/domain/entities/job.py`
- [x] Commit: `feat(spec-056): add chunking configuration domain models`

### 1-2. Semantic Chunker 구현
- [x] `LangChainSemanticChunker` 구현: `app/infrastructure/chunker/semantic_chunker.py`
- [x] `ChunkerFactory` 구현 및 전략 패턴 적용: `app/infrastructure/chunker/chunker_factory.py`
- [x] 단위 테스트 작성 및 패스: `tests/unit/infrastructure/chunker/test_semantic_chunker.py`
- [x] Commit: `feat(spec-056): implement semantic chunking logic and factory`

---

## Task 2: API Integration & UI Implementation
### 2-1. API DTO 및 Endpoints 강화
- [x] `IngestRequest` 확장 및 `JobResponse`에 `docs_ids` 추가: `app/interfaces/api/v1/dto/`
- [x] `Ingestion` 서비스 비동기 로직 수정: `app/application/services/ingestion.py`
- [x] 통합 테스트(API Flow) 검증: `tests/integration/functional/test_ingestion_with_semantic.py`
- [x] Commit: `feat(spec-056): integrate semantic chunking into ingestion pipeline`

### 2-2. Admin Dashboard UI 업데이트
- [x] 청킹 파라미터 제어용 UI 위젯 추가: `admin/pages/0_Ingestion_Management.py`
- [x] Commit: `feat(spec-056): add chunking settings to admin ingestion page`

---

## Task 3: PR Creation & Archiving (Completed)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest tests/unit tests/integration`
- [x] `walkthrough.md` 및 `pr_description.md` 작성 및 아카이브: `specs/056-semantic-chunking-upgrade/`
- [x] PR 생성 및 Merged: `#62`
