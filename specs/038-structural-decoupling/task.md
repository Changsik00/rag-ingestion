# Task List: Spec-038 (Structural Decoupling)

## Progress
- [x] Spec 번호 확정 (038)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

## Task 1: Foundation & Physical Separation
### 1-1. Physical Separation
- [x] `app/admin` -> `admin/` 디렉토리 이동 및 `sys.path` 정리
- [x] Dockerfile 및 `docker-compose.yml` 관리자 설정 격리 (DB 접근 차단)
- [x] Commit: `chore(spec-038): physical separation and infrastructure isolation`

### 1-2. Base Backend API Setup
- [x] `app/interfaces/api/v1/endpoints/admin/` 라우터 패키지 구조 생성
- [x] `app/main.py`에 전체 관리자용 라우터 등록
- [x] Commit: `feat(spec-038): setup admin api router foundation`

## Task 2: Granular API Implementation (Backend)
### 2-1. Storage Integrity & Recovery API
- [x] **TDD Warming up**: `tests/integration/api/admin/test_storage.py` 작성
- [x] `GET /storage/stats`, `GET /storage/reports` 구현
- [x] `GET /storage/documents/{id}/diagnostic` 및 `preview-context` 구현
- [x] `POST /storage/documents/{id}/sync`, `enrich` 구현
- [x] `POST /storage/sync-all` (Async) 및 `GET /sync-jobs/{id}` (Progress) 구현
- [x] Commit: `feat(spec-038): implement exhaustive storage diagnostic and recovery apis`

### 2-2. Graph & RAG Session API
- [x] **TDD Warming up**: `tests/integration/api/admin/test_rag.py` 작성
- [x] `POST /graph/query` (Neo4j Graph to Agraph JSON conversion) 구현
- [x] **Knowledge Source**: `GET /rag/documents/autocomplete` (검색어 기반 문서 추천) 구현
- [x] **Advanced Settings**: `POST /rag/sessions` (Reset), `DELETE /history` (Clear), `POST /config` 구현
- [x] `POST /rag/sessions/{id}/ask` (Streaming response) 구현
- [x] `GET /rag/sessions/{id}/trace` 및 `POST /resume` (HITL) 구현
- [x] `POST /feedback` 구현
- [x] Commit: `feat(spec-038): implement interactive rag session, autocomplete and advanced settings apis`

## Task 3: Thin Client Refactoring (Frontend & Tests)
### 3-1. API Client Implementation
- [x] `admin/utils/api_client.py` 구현 (`httpx` singleton with error handling)
- [x] Commit: `feat(spec-038): implement streamlit-ready api client`

### 3-2. Page-by-Page Migration (Zero Import)
- [x] Page 0 (Jobs) & Page 5 (Storage) API 연동
- [x] Page 1 (Graph) API 연동
- [x] Page 4 (Playground):
    - Knowledge Source: `st.selectbox` + API Autocomplete 연동
    - Advanced Settings: Clear/Reset 버튼 API 연동
    - Main Chat: API 기반 대화 처리 및 HITL 연동
- [x] 2, 3 (HITL/Trace) 보조 기능 통합 및 직접 import 전수 제거
- [x] Commit: `refactor(spec-038): 100% thin client transformation of all dashboard pages`

### 3-3. Test Refactoring (Zero Import Enforcement)
- [x] 기존 Admin UI 테스트 (`tests/admin/`) 검수: `from app.` 구문 색출
- [x] 모든 UI 테스트를 `api_client` Mocking 또는 통합 테스트로 전환
- [x] Commit: `test(spec-038): refactor all admin tests to depend only on apis`

## Task 4: PR Creation
- [x] Code Quality: `uv run ruff check . --fix && uv run ruff format .`
- [x] Full Tests: `uv run pytest -v` (207 passed)
- [x] Walkthrough 작성: `specs/038-structural-decoupling/walkthrough.md`
- [x] PR Description 작성: `specs/038-structural-decoupling/pr_description.md`
- [x] Create PR: `gh pr create` -> [PR #39](https://github.com/Changsik00/rag-ingestion/pull/39)

## Task 6: Debugging & Stabilization
- [/] Fix HITL 404: Add missing endpoints to `app/interfaces/api/v1/endpoints/admin/jobs.py`
- [ ] Fix SQLite 500: Solve "database disk image is malformed" error
- [ ] Verify Streamlit stability: Correct internal 404s if necessary

## Summary
**총 Task**: 5개 대분류 + 디버깅
**최종 상태**: 아키텍처 격리 후 실제 운영 환경 디버깅 중
**완료 일자**: 2026-01-26
