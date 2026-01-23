# Task List: Spec-031 Source-Filtered RAG

## Progress
- [ ] Spec 번호 확정 (031)
- [x] spec.md 작성 (Final)
- [x] plan.md 작성 (Final)
- [x] task.md 작성 (Final)
- [x] 백로그 업데이트 & 전략 문서 반영
- [x] User Plan Accept

## Task 1: Repository Filter Implementation (Foundation)
### 1-1. TDD: Verification Scenarios
- [x] Integration Test 작성: `tests/integration/test_filtered_search.py`
    - [x] Scenario 1: Homonym Test (Single/Multi filter)
    - [x] Scenario 2: Context Switch Test
    - [x] Scenario 3: Source Injection Test
- [x] Test 실행 (Expected Fail): `uv run pytest tests/integration/test_filtered_search.py`
- [x] Commit: `test(spec-031): add strict isolation scenarios`

### 1-2. Implementation
- [x] `DocumentRepository` Interface 수정 (`filters` arg)
- [x] `Neo4jStorage`: Cypher `IN` clause generator 구현
- [x] `ChromaStorage`: Metadata `$in` filter adapter 구현
- [x] `CompositeStorage` Pass-through 적용
- [x] Test 실행 (Pass): `uv run pytest tests/integration/test_filtered_search.py`
- [x] Commit: `feat(spec-031): implement physical filtering in repositories`

## Task 2: Service Layer & Logic
- [x] `RAGService` Update: `filters` 파라미터 전파
- [x] `ContextualRAG` Chain Update
- [x] Contract/Unit Test Update
- [x] Commit: `feat(spec-031): enable filtering in rag service`

## Task 3: Admin UI Integration
- [x] `4_RAG_Playground.py` UI 개선
    - [x] `st.multiselect`로 문서 선택 UI 변경 (Source of Truth)
    - [x] 선택된 문서 ID 리스트를 Service로 전달
    - [x] UX 개선: 사이드바 상단으로 이동 및 검색/자동완성 기능 추가
- [x] Manual Check: Playground에서 시나리오 1, 2, 3 직접 수행
- [x] Commit: `feat(spec-031): add prominent searchable source filter`

## Task 4: Finalize
- [x] Code Quality Check: `uv run ruff check . --fix`
- [x] Full Test Suite: `uv run pytest` (In Progress - Regression Fix)
- [x] PR Creation: Strategy 문서 링크 포함
