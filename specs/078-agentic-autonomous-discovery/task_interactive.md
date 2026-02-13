# Task List: Spec-078

## Progress
- [/] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

---

## Task 1: Environment & Google Search Client
### 1-1. Google Settings & DI
- [x] `.env.example` 업데이트 (`GOOGLE_CSE_ID` 추가)
- [x] `app/bootstrap/di.py`에 `GoogleSearchClient` 등록
- [x] Test 작성: `tests/unit/infrastructure/test_di_configuration.py` (설정 로드 확인)

### 1-2. Google Search Client Implementation
- [x] Test 작성: `tests/unit/infrastructure/test_google_search.py`
- [x] 구현: `app/infrastructure/external_api/google_search_client.py`
- [x] 검증: Mock 응답을 이용한 파싱 로직 테스트

---

## Task 2: Discovery Service (Core Logic)
### 2-1. Discovery Domain Service
- [x] Test 작성: `tests/unit/domain/services/test_discovery_service.py` (BFS 로직 검증)
- [x] 구현: `app/domain/services/discovery_service.py`
  - `start_discovery(topic)` 메소드
  - URL Queue 및 Visited Set 관리
  - Depth 제어

### 2-2. Integration with Scraper
- [x] Test 작성: `tests/integration/test_discovery_flow.py` (skipped in favor of E2E verification)
- [x] 구현: 기존 `Scraper` 서비스를 호출하여 콘텐츠 수집 연결

---

## Task 3: Interface & Tooling
### 3-1. API Implementation
- [x] Test 작성: `tests/unit/interfaces/api/test_discovery_routes.py`
- [x] 구현: `app/interfaces/api/v1/discovery_routes.py`
- [x] `main.py`에 라우터 등록

### 3-2. DiscoveryTool (LangGraph)
- [x] Test 작성: `tests/unit/interfaces/tools/test_discovery_tool.py`
- [x] 구현: `app/interfaces/tools/discovery_tool.py` (`BaseTool` 상속)
- [x] Agent 연동 가이드 작성

---

## Task 4: Integration & Verification
### 4-1. Verification
- [x] 전체 Test Suite 실행: `uv run pytest`
- [x] Manual Verification (Google Mock Response 확인)

### 4-2. Documentation
- [x] `walkthrough.md` 작성
- [x] `pr_description.md` 작성
- [x] PR 생성 및 Review 요청

---

## Task N: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/078-agentic-autonomous-discovery/walkthrough.md`
- [x] **PR Description 작성**: `specs/078-agentic-autonomous-discovery/pr_description.md`
- [x] **Archive Commit**: 위 파일을 `specs/`에 커밋
- [x] Create PR: `gh pr create`

## Summary
**총 Task**: 3개 그룹 + 마무리
**예상 커밋 수**: 6~8개
**현재 진행**: Planning
