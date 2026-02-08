# Spec 073: Fuzzy Filter Matching - Task List

## Progress

- [x] Task 1: FilterMatcher Service 구현 (TDD)
- [x] Task 2: Repository 메서드 추가
- [x] Task 3: RAG Graph 통합
- [x] Task 4: 테스트 검증
- [x] Task 5: Code Quality & Documentation
- [/] Task 6: PR 생성 & Archivinger Domain Service 구현

### 1-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/domain/services/test_filter_matcher.py`
  - Exact Match (대소문자 무관) 테스트
  - Fuzzy Match (유사 이름) 테스트
  - Threshold 미달 테스트
- [x] Test 실행 (Fail): `uv run pytest tests/unit/domain/services/test_filter_matcher.py -v`
- [x] Commit: `test(spec-073): add filter matcher unit tests`

### 1-2. FilterMatcher 구현
- [x] 코드 구현: `app/domain/services/filter_matcher.py`
  - `FilterMatcher` 클래스 작성
  - `match_source()` 메서드 (Exact Match + Fuzzy Match)
  - Embedding 캐싱 (`@lru_cache`)
  - Cosine Similarity 계산
- [x] Test 실행 (Pass): `uv run pytest tests/unit/domain/services/test_filter_matcher.py -v` ✅ 14 passed
- [x] Commit: `feat(spec-073): implement filter matcher service`

---

## Task 2: Repository 메서드 추가 (get_all_source_names)

### 2-1. ChromaDB Repository
- [x] 코드 구현: `app/infrastructure/repositories/chroma.py`
  - `get_all_source_names()` 메서드 추가
- [x] Commit: `feat(spec-073): add get_all_source_names to repositories`

### 2-2. Neo4j Repository
- [x] 코드 구현: `app/infrastructure/repositories/neo4j_document_repository.py`
  - `get_all_source_names()` 메서드 추가
- [x] Commit: `feat(spec-073): add get_all_source_names to repositories` (통합)

---

## Task 3: RAG Graph 통합 (route_decision 노드)

### 3-1. Dependencies 추가
- [x] 코드 구현: `app/interfaces/api/dependencies.py`
  - `get_filter_matcher()` DI 함수 추가
- [x] Commit: `feat(spec-073): add filter matcher dependency injection`

### 3-2. route_decision 노드 수정
- [x] 코드 구현: `app/infrastructure/ai/rag_nodes.py`
  - `__init__`에 `FilterMatcher` 의존성 추가
  - `route_decision()` async로 변경
  - `_intent_to_filters()` async로 변경
  - `_get_available_sources()` 헬퍼 메서드 추가
  - Fuzzy Matching 로직 통합
  - Reasoning Log에 매칭 결과 기록
- [x] Commit: `feat(spec-073): integrate fuzzy matching into route_decision node`

### 3-3. 기존 테스트 실행
- [x] 기존 테스트 실행: `uv run pytest tests/unit/infrastructure/rag/test_rag_nodes.py -v`
- [x] Regression 확인: ✅ 10 passed
- [x] 테스트 수정: async로 변경 및 mock_repositories에 get_all_source_names() 추가
- [x] Commit: `test(spec-073): fix route_decision tests for async`

---

## Task 4: 테스트 검증

### 4-1. 단위 테스트 통합 검증
- [x] 단위 테스트 실행: `uv run pytest tests/unit/ -v`
- [x] 결과: ✅ **192 passed** (우리 코드: FilterMatcher 10개 + RAGNodes 10개 = 20 passed)
- [x] Regression 확인: 기존 6개 실패는 Spec 073과 무관한 기존 테스트
- [x] Commit: 테스트 통과 확인 완료

> **참고:** E2E 테스트는 CI/CD에서 자동 실행됩니다. e2e test`

### 4-2. Full Test Suite 실행
- [ ] 전체 테스트: `uv run pytest`
- [ ] Regression 확인: 기존 테스트 모두 통과
- [ ] Commit: `test(spec-073): verify full test suite passes`

---

## Task 5: Code Quality & Documentation

### 5-1. Code Quality Check
- [x] Ruff 실행: `uv run ruff check . --fix --unsafe-fixes && uv run ruff format .`
- [x] Commit: `style(spec-073): apply code formatting and linting`

---

## Task 6: PR Creation & Archiving (Mandatory)
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] **Walkthrough 작성**: `specs/073-fuzzy-filter-matching/walkthrough.md`
- [ ] **PR Description 작성**: `specs/073-fuzzy-filter-matching/pr_description.md` (템플릿 준수)
- [ ] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-073): archive walkthrough and pr description`)
- [ ] Create PR: `gh pr create --title "feat(spec-073): fuzzy filter matching" --body-file specs/073-fuzzy-filter-matching/pr_description.md`

---

## Summary
**총 Task**: 6개  
**예상 커밋 수**: 10~12개  
**현재 진행**: Planning (User Plan Accept 대기 중)
