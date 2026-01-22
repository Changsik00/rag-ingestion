# Task List: Spec-028 (Agentic MCP Server)

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트
- [x] User Plan Accept

## Task 1: 환경 설정 및 의존성 관리
### 1-1. Dependency Setup
- [x] `pyproject.toml`: `mcp` 라이브러리 추가
- [x] `uv sync` 실행 및 lock 파일 갱신
- [x] Commit: `chore(spec-028): add mcp dependency`

## Task 2: MCP 서버 구현
### 2-1. Server Setup & Tools
- [ ] Test Case 작성: `tests/unit/interfaces/test_mcp_server.py` (Mocking Service)
- [ ] Test 실행 (Fail)
- [ ] 코드 구현: `app/interfaces/mcp_server.py`
    - [ ] `FastMCP` 초기화
    - [ ] `ingest_url` 구현 (Service 연동)
    - [ ] `search_knowledge_base` 구현 (Service 연동)
- [ ] Test 실행 (Pass)
- [ ] Commit: `feat(spec-028): implement mcp server and tools`

## Task 3: PR Creation & Delivery
- [ ] Code Quality Check: `uv run ruff check . --fix`
- [ ] Manual Verification: `mcp-inspector` 테스트 (Walkthrough에 스크린샷 포함)
- [ ] Create PR: `gh pr create`
- [ ] Summary in Task.md

## Summary
**총 Task**: 3개
**예상 커밋 수**: 3~4개
