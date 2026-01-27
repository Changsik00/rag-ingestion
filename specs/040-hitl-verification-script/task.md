# Task List: Spec 040 - Real-World HITL Verification Script

## Progress
- [x] Spec 번호 확정 (040)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] User Plan Accept
- [/] Feature 브랜치 생성: `feature/spec-040-hitl-script`

---

## Task 1: Environment & Skeleton Setup

### 1-1. Script Skeleton
- [ ] `scripts/verify_hitl_real.py` 파일 생성
- [ ] 기본 Imports 및 `load_dotenv()` 설정
- [ ] **Commit**: `chore(spec-040): create script skeleton`

### 1-2. Real Component Integration
- [ ] `ChatGoogleGenerativeAI`, `AdminAgent`, `MemorySaver` 초기화
- [ ] **Test Execution**: 단순 Hello World 질문응답 확인
- [ ] **Commit**: `feat(spec-040): setup real agent components`

---

## Task 2: Interactive HITL Logic Implementation

### 2-1. Streaming & Toggle Logic
- [ ] `hitl_enabled` 입력(Toggle) 처리 로직 추가
- [ ] `workflow.astream()` 호출 시 `hitl_enabled` state 전달
- [ ] **Commit**: `feat(spec-040): implement hitl toggle and streaming`

### 2-2. Interrupt & Resume
- [x] `snapshot.next` 확인하여 Interrupt 감지 및 알림
- [x] `input()`으로 Feedback 수신 및 `update_state`
- [x] `workflow.invoke(None)` 호출로 Resume 구현
- [x] **Commit**: `feat(spec-040): implement interrupt and resume logic`

---

## Task 3: Verification & Refinement

- [x] **Scenario A (Off)**: HITL 꺼진 상태에서 Non-stop 실행 확인
- [x] **Scenario B (On)**: HITL 켜진 상태에서 Interrupt/Resume 확인
- [x] **Commit**: `test(spec-040): verify hitl scenarios`

---

## Task 4: PR Creation

- [ ] Code Quality: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Full Tests: `uv run pytest -v` (기존 테스트 회귀 확인)
- [ ] Walkthrough 작성: `specs/040-hitl-verification-script/walkthrough.md`
- [ ] PR Description 작성: `specs/040-hitl-verification-script/pr_description.md`
- [ ] Create PR: `gh pr create --title "test(spec-040): add real-world hitl verification script" --body-file specs/040-hitl-verification-script/pr_description.md`


---

## Summary
**총 Task**: 4개 카테고리 (7개 세부 항목)
**예상 커밋 수**: 6~7개
**현재 진행**: Planning 완료, User Approval 대기 중
