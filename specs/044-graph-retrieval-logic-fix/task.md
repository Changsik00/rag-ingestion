# Task List: Spec-044

## Progress
- [x] Spec 번호 확정 (044)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

## Task 1: IntentClassifier Entity Extraction
### 1-1. Model & Prompt Update
- [x] Test Case 작성: `tests/unit/test_intent_classifier.py` (Entity 추출 검증)
- [x] `app/infrastructure/brain/nodes.py` 수정: `IntentResult` 모델에 `entities` 필드 추가
- [x] Prompt 템플릿 수정: 고유명사 추출 지시 추가
- [x] Test 실행 및 Pass 확인
- [x] Commit: `feat(spec-044): add entity extraction to intent classifier`

## Task 2: Neo4j Repository Extension
### 2-1. Graph Traversal Logic
- [x] Test Case 작성: `tests/integration/test_neo4j_graph_retrieval.py`
- [x] `app/infrastructure/store/neo4j_document_repository.py` 수정: `find_subgraph_by_entities` 구현
- [x] Test 실행 및 Pass 확인 (실제 Neo4j 컨테이너 연동)
- [x] Commit: `feat(spec-044): implement subgraph retrieval by entities`

## Task 3: RAG Service Integration
### 3-1. Logic Wiring
- [ ] `app/domain/rag/service.py` 수정: Intent 결과의 Entity를 사용하여 Graph 조회 및 Context 병합
- [ ] Test 실행: End-to-End 로직 검증 (`test_rag_flow.py` 등)
- [ ] Commit: `feat(spec-044): integrate graph context into rag pipeline`

## Task 4: PR Creation
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] Create PR: `gh pr create --title "feat(spec-044): graph retrieval logic fix" ...`

## Summary
**총 Task**: 3개 (주요 개발) + PR
**예상 커밋 수**: 4~5개
