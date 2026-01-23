# Task List: Spec 032 - Router & Intent Classifier

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept
- [x] Feature 브랜치 생성: `feature/032-router-intent-classifier`

---

## Task 1: Intent Classifier Domain Service

### 1-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/domain/test_intent_classifier.py` (7개 시나리오)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/domain/test_intent_classifier.py -v`
- [x] Commit: `test(spec-032): add intent classifier test cases`

### 1-2. Implementation
- [x] Pydantic Schema 정의: `app/domain/schemas/intent.py`
- [x] Domain Service 구현: `app/domain/services/intent_classifier.py`
- [x] Test 실행 (Pass): `uv run pytest tests/unit/domain/test_intent_classifier.py -v`
- [x] Commit: `feat(spec-032): implement intent classifier domain service`

---

## Task 2: RAG Service Integration

### 2-1. TDD Warming up
- [x] Integration Test 작성: `tests/integration/bdd/test_intent_routing.py`
- [x] Test 실행 (Fail): `uv run pytest tests/integration/bdd/test_intent_routing.py -v`
- [x] Commit: `test(spec-032): add intent routing integration tests`

### 2-2. Implementation
- [x] RAGService 확장: `app/domain/services/rag_service.py`
- [x] Dependency Injection: `app/interfaces/api/dependencies.py`
- [x] Test 실행 (Pass): `uv run pytest tests/unit/domain/test_intent_classifier.py -v`
- [x] Commit: `feat(spec-032): integrate intent classifier into rag service`

---

## Task 3: Admin Dashboard Debug View

- [ ] Streamlit UI 추가: `app/admin/pages/4_RAG_Playground.py`
- [ ] Intent Debug Expander 구현
- [ ] Manual Verification (로컬 테스트)
- [ ] Commit: `feat(spec-032): add intent routing debug view`

---

## Task 4: PR Creation

- [ ] Code Quality: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Full Tests: `uv run pytest -v`
- [ ] Walkthrough 작성: `specs/032-router-intent-classifier/walkthrough.md`
- [ ] PR Description 작성: `specs/032-router-intent-classifier/pr_description.md`
- [ ] Create PR: `gh pr create --title "feat(spec-032): router and intent classifier" --body-file specs/032-router-intent-classifier/pr_description.md`

---

## Summary

**총 Task**: 4개  
**예상 커밋 수**: 7개  
**현재 진행**: Task 1-1 완료 (테스트 작성)
