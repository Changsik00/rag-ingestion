# Task List: Spec-055 RAG Precision & Advanced Settings

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: API DTO 및 엔드포인트 개선 (DTO First)
### 1-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/interfaces/api/v1/dto/test_rag_dto.py` (Request Validation Test)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/interfaces/api/v1/dto/test_rag_dto.py`
- [x] Commit: `test(spec-055): add unit tests for ChatRequest dto`

### 1-2. Implementation
- [x] 코드 구현: `app/interfaces/api/v1/dto/rag.py`에 `ChatRequest` 및 `AdvancedSettings` 추가
- [x] Test 실행 (Pass): `uv run pytest tests/unit/interfaces/api/v1/dto/test_rag_dto.py`
- [x] Commit: `feat(spec-055): implement ChatRequest and AdvancedSettings DTOs`

---

## Task 2: 엔드포인트 및 RAG Agent 연동
### 2-1. TDD Warming up
- [x] Test Case 작성: `tests/integration/functional/test_api_endpoints.py` (새로운 Payload 전송 테스트)
- [x] Test 실행 (Fail): `uv run pytest tests/integration/functional/test_api_endpoints.py` (422 Unprocessable Entity 예상)
- [x] Commit: `test(spec-055): update api tests to use new ChatRequest payload`

### 2-2. Implementation
- [x] 코드 수정: `app/interfaces/api/v1/endpoints/rag.py`의 `ask_agent` 시그니처 변경 및 Config 주입 로직
- [x] Test 실행 (Pass): `uv run pytest tests/integration/functional/test_api_endpoints.py`
- [x] Commit: `feat(spec-055): update ask_agent endpoint to accept ChatRequest`

---

## Task 3: Admin Dashboard UI 고도화
### 3-1. Implementation
- [x] 코드 구현: `admin/pages/4_RAG_Playground.py`에 Advanced Settings Expander 및 Input Widget 구현
- [x] 연동 : API 호출 시 `advanced_settings` 딕셔너리 구성하여 payload에 포함

### 3-2. Verification
- [x] Manual Check: Dashboard에서 Top-K 조절 후 검색 결과 변화 확인
- [x] Commit: `feat(spec-055): add advanced settings UI to rag playground`

---

## Task 4: PR 생성 및 문서화 (Mandatory)
<!-- 이 단계는 모든 작업 완료 후 수행합니다. -->
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/055-rag-precision-advanced-settings/walkthrough.md`
- [x] **PR Description 작성**: `specs/055-rag-precision-advanced-settings/pr_description.md` (템플릿 준수)
- [x] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-055): archive walkthrough and pr description`)
- [x] Create PR: `gh pr create --title "feat(spec-055): rag precision and advanced settings" --body-file specs/055-rag-precision-advanced-settings/pr_description.md`

## Summary
**총 Task**: 4개  
**예상 커밋 수**: 8개 내외  
**현재 진행**: Completed
