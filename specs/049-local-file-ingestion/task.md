# Task List: Spec-049 Local File Ingestion

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Foundation & File Processing
### 1-1. Branch Creation
- [x] 브랜치 생성: `git checkout -b feature/049-local-file-ingestion`

### 1-2. TDD: File Processor
- [x] 의존성 추가: `uv add pymupdf python-magic-bin`
- [x] Test Case 작성: `tests/unit/test_file_processor.py` (PDF/TXT/MD 파싱 검증)
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_file_processor.py`
- [x] Commit: `test(spec-049): add test case for file processor`

### 1-3. Implementation: File Processor (Chunked)
- [x] `app/domain/services/file_processor.py` 제너레이터 방식으로 리팩토링
- [x] `extract_segments` 구현 (PDF 페이지별, TXT 청크별)
- [x] Commit: `feat(spec-049): refactor file processor for chunked extraction`

---

## Task 2: API & Service Integration
### 2-1. Ingestion Service Update (Loop Processing)
- [x] `IngestionService.process_job` 리팩토링: 파일 처리 시 세그먼트 루프 적용
- [x] 세그먼트별 Semantic Extraction 및 Graph Indexing 연동 확인
- [x] Commit: `feat(spec-049): support iterative processing of file segments`

### 2-2. API Endpoint Development
- [x] `app/api/endpoints/ingestion.py`에 `POST /ingest/file` 추가 (main.py에 통합)
- [x] Commit: `feat(spec-049): add multipart file upload endpoint`

---

## Task 3: Admin UI & Playground
### 3-1. Management UI Update
- [x] `admin/pages/0_Ingestion_Management.py` 생성 및 연동
- [x] `admin/utils/api_client.py` multipart 지원 추가
- [x] Commit: `feat(spec-049): add file upload to management dashboard`

### 3-2. Playground Integration
- [x] `admin/pages/4_RAG_Playground.py` 사이드바 파일 업로드 위젯 추가
- [x] Commit: `feat(spec-049): support direct file upload in playground`

---

## Task 4: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/049-local-file-ingestion/walkthrough.md`
- [ ] **PR Description 작성**: `specs/049-local-file-ingestion/pr_description.md`
- [x] **Archive Commit**: 위 파일들을 커밋 (`docs(spec-049): archive walkthrough and pr description`)
- [x] Create PR: `gh pr create --title "feat(spec-049): local file ingestion (pdf, txt, md) support" --body-file specs/049-local-file-ingestion/pr_description.md`

## Summary
---

---

## Task 5: Support Multiple File Uploads & Drag-and-Drop (Enhancement)
- [x] `app/interfaces/api/main.py`: `ingest_file` 엔드포인트를 다중 파일 수락 가능하도록 리팩토링
- [x] `admin/pages/0_Ingestion_Management.py`: `st.file_uploader`에 `accept_multiple_files=True` 적용 및 루프 처리
- [x] `admin/pages/4_RAG_Playground.py`: 사이드바 업로드 위젯 다중 파일 지원
- [x] 다중 파일 업로드 시 개별 Job 생성 확인 및 검증
- [x] Commit: `feat(spec-049): support multi-file upload and drag-and-drop UI`

## Task 6: Resolve Docker Build & Networking Issues (Hotfix)
- [x] `pyproject.toml`: `python-magic-bin` 제거 및 `python-magic` 추가
- [x] `Dockerfile.backend`, `Dockerfile.admin`: `libmagic1` 시스템 필수 패키지 추가
- [x] `app/interfaces/api/main.py`: `MultiAsyncIngestResponse` 누락된 임포트 추가 (NameError 해결)
- [x] `docker-compose.yml`: `ADMIN_API_URL` 및 `NEO4J_URI` 호스트명 동기화 및 APOC 권한 해제 (`unrestricted`)
- [x] Commit: `fix(spec-049): resolve backend startup NameError and neo4j permission issues`

## Task 7: Fix Job Persistence & Retrieval
- [x] `app/infrastructure/storage/neo4j_job_repository.py`: `raw_content`, `filename`, `docs_ids` 데이터 누락 수정
- [x] 검증: 파일 업로드 후 백엔드 로그에서 `Processing local file` 확인
- [x] Commit: `fix(spec-049): resolve backend NameError, neo4j config, and job persistence`

## Task 8: Fix `AttributeError` in semantic extraction and debug retrieval prioritization.
    *   Renamed `extract_metadata` to `aextract_metadata`.
    *   Handled `thread_id` fallback in `LangGraphAdapter`.
    *   Improved interleaving of keyword and vector results in RAG.
## Task 9: Optimize hybrid search and reranking, including final verification.
    *   Expanded reranking window to 15 candidates.
    *   Explicitly prioritized Knowledge Graph context in generate_answer prompt.
    *   Added extensive debug logging for retrieval and storage.
- [x] 최종 검증: "네오사피엔스" 질문 시 업로드된 계약서 내용 기반 정확한 답변 확인

## Task 10: Critical Fix - Storage ID Mismatches & Data Corruption [Hotfix]
- [x] `app/infrastructure/storage/neo4j_document_repository.py`: `Chunk` nodes missing `id` (mismatch with `chunk_id`) fixed.
- [x] `app/infrastructure/storage/neo4j_job_repository.py`: Binary `raw_content` encoded as Base64 to prevent corruption (`????`).
- [x] `app/domain/entities/job.py`: `raw_content` excluded from API serialization to prevent Unicode errors.
- [x] System Verification: Full RAG pipeline test with "Neosapiens" contract.

## Summary
**총 Task**: 10개  
**예상 커밋 수**: 15개 이상  
**현재 진행**: All tasks completed & Verified
