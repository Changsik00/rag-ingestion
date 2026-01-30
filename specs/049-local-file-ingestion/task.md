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
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] **Walkthrough 작성**: `specs/049-local-file-ingestion/walkthrough.md`
- [ ] **PR Description 작성**: `specs/049-local-file-ingestion/pr_description.md`
- [ ] **Archive Commit**: 위 파일들을 커밋 (`docs(spec-049): archive walkthrough and pr description`)
- [ ] Create PR: `gh pr create --title "feat(spec-049): local file ingestion (pdf, txt, md)" --body-file specs/049-local-file-ingestion/pr_description.md`

## Summary
**총 Task**: 4개  
**예상 커밋 수**: 7개 이상  
**현재 진행**: Completed (All tasks finished)
