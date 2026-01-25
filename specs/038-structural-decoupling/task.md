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
- [ ] `app/interfaces/api/v1/endpoints/admin/` 라우터 패키지 구조 생성
- [ ] `app/main.py`에 전체 관리자용 라우터 등록
- [ ] Commit: `feat(spec-038): setup admin api router foundation`

## Task 2: Granular API Implementation (Backend)
### 2-1. Storage Integrity & Recovery API
- [ ] **TDD Warming up**: `tests/integration/api/admin/test_storage.py` 작성
- [ ] `GET /storage/stats`, `GET /storage/reports` 구현
- [ ] `GET /storage/documents/{id}/diagnostic` 및 `preview-context` 구현
- [ ] `POST /storage/documents/{id}/sync`, `enrich` 구현
- [ ] `POST /storage/sync-all` (Async) 및 `GET /sync-jobs/{id}` (Progress) 구현
- [ ] Commit: `feat(spec-038): implement exhaustive storage diagnostic and recovery apis`

### 2-2. Graph & RAG Session API
- [ ] **TDD Warming up**: `tests/integration/api/admin/test_rag.py` 작성
- [ ] `POST /graph/query` (Neo4j Graph to Agraph JSON conversion) 구현
- [ ] **Knowledge Source**: `GET /rag/documents/autocomplete` (검색어 기반 문서 추천) 구현
- [ ] **Advanced Settings**: `POST /rag/sessions` (Reset), `DELETE /history` (Clear), `POST /config` 구현
- [ ] `POST /rag/sessions/{id}/ask` (Streaming response) 구현
- [ ] `GET /rag/sessions/{id}/trace` 및 `POST /resume` (HITL) 구현
- [ ] `POST /feedback` 구현
- [ ] Commit: `feat(spec-038): implement interactive rag session, autocomplete and advanced settings apis`

## Task 3: Thin Client Refactoring (Frontend & Tests)
### 3-1. API Client Implementation
- [ ] `admin/utils/api_client.py` 구현 (`httpx` singleton with error handling)
- [ ] Commit: `feat(spec-038): implement streamlit-ready api client`

### 3-2. Page-by-Page Migration (Zero Import)
- [ ] Page 0 (Jobs) & Page 5 (Storage) API 연동
- [ ] Page 1 (Graph) API 연동
- [ ] Page 4 (Playground):
    - Knowledge Source: `st.selectbox` + API Autocomplete 연동
    - Advanced Settings: Clear/Reset 버튼 API 연동
    - Main Chat: API 기반 대화 처리 및 HITL 연동
- [ ] 2, 3 (HITL/Trace) 보조 기능 통합 및 직접 import 전수 제거
- [ ] Commit: `refactor(spec-038): 100% thin client transformation of all dashboard pages`

### 3-3. Test Refactoring (Zero Import Enforcement)
- [ ] 기존 Admin UI 테스트 (`tests/admin/`) 검수: `from app.` 구문 색출
- [ ] 모든 UI 테스트를 `api_client` Mocking 또는 통합 테스트로 전환
- [ ] Commit: `test(spec-038): refactor all admin tests to depend only on apis`

## Task 4: Verification & PR Creation
### 4-1. QA & Verification
- [ ] **Import Guard**: `grep -r "from app." admin/` 실행하여 의존성 제로 확인
- [ ] 통합 테스트 실행 (`tests/integration/api/admin/`) - All Pass 확인
- [ ] `docker-compose` 환경에서의 격리 기능 최종 검증
- [ ] Commit: `chore(spec-038): finalize architectural isolation and verify`

### 4-2. Documentation & PR
- [ ] Walkthrough.md 작성
- [ ] Code Quality Check: `ruff check . --fix && ruff format .`
- [ ] PR 생성
- [ ] Commit: `docs(spec-038): add walkthrough and finalize spec artifacts`

## Summary
**총 Task**: 4개 대분류 (15개 이상 상세 API 처리)
**예상 커밋 수**: 12~15개
