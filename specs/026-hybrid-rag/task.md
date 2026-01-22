# Task List: Spec-026 (Graph-Enhanced RAG)

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성 (In-sil-jik-go & Graph Strategy)
- [x] plan.md 작성 (RAGService & MMR Included)
- [x] task.md 작성
- [x] User Plan Accept

## Task 1: Neo4j Search & Graph Enhancement
### 1-1. Fulltext Index (TDD)
- [x] Test 작성: `tests/integration/test_neo4j_repository.py` (Search Fail 확인)
- [x] Test 실행 (Fail): `uv run pytest tests/integration/test_neo4j_repository.py`
- [x] Implementation: `create_fulltext_index` & `search` in `Neo4jDocumentRepository`
- [x] Test 실행 (Pass)
- [x] Commit: `feat(spec-026): implement neo4j fulltext search`

### 1-2. Graph Traversal (SubGraph)
- [x] Test 작성: `tests/integration/test_neo4j_graph_retrieval.py`
- [x] Implementation: `Neo4jGraphRepository.get_subgraph`
- [x] Test 실행 (Pass)
- [x] Commit: `feat(spec-026): implement graph traversal for context`

## Task 2: Vector DB Upgrade (Diversity)
### 2-1. MMR Search (TDD)
- [x] Test 작성: `tests/integration/test_chroma_repository.py` (Diversity Check)
- [x] Test 실행 (Fail): kNN vs MMR 결과 비교
- [x] Implementation: `ChromaStorage.search_mmr` 구현
- [x] Test 실행 (Pass)
- [x] Commit: `feat(spec-026): implement chroma mmr search`

## Task 3: Domain Service & Orchestration
### 3-1. RAGService Implementation
- [x] `app/domain/services/rag_service.py` 생성
- [x] Logic: Rewrite -> Parallel Hybrid Search -> Fact/Chunk Merge -> Citation Format
- [x] Commit: `refactor(spec-026): introduce RAGService domain layer`

## Task 4: UI & Documentation
### 4-1. Playground Integration
- [x] `4_RAG_Playground.py`: `RAGService` 연동
- [x] Debug View: Graph Faact 표시 기능 추가
- [x] Commit: `ui(spec-026): integrate hybrid rag into playground`

### 4-2. Documentation (Design Guide)
- [x] `docs/design_guides/004-graph-rag-strategy.md` 작성
    - [x] kNN vs MMR 설명
    - [x] Graph Context Injection 아키텍처 다이어그램
- [x] Commit: `docs(spec-026): add graph rag strategy guide`

## Task 5: Verification & Integration Tests
### 5-1. Automated Integration Tests
- [x] `tests/integration/test_hybrid_retrieval.py` 작성
    - [x] Scenario: Vector + Keyword 결과 병합 확인
    - [x] Scenario: Graph Fact Injection 확인
- [x] `uv run pytest tests/integration/test_hybrid_retrieval.py` 실행 및 통과
- [x] Commit: `test(spec-026): add hybrid retrieval integration tests`

### 5-2. Manual Verification
- [x] **Playground Test**: "일론 머스크" 검색 시 Graph Fact(`FOUNDED` 등)가 Debug View에 뜸
- [x] **Citation Check**: 답변에 `[Wiki]` 등 출처가 정확히 달리는지 확인

## Task 6: Final Review & Delivery
- [x] **Linting & Quality Check**
    - [x] `uv run ruff check . --fix`
- [x] **Documentation & History**
    - [x] Update `walkthrough.md` with Verification Screenshots
    - [x] Update `backlog/queue.md` (Mark Spec 026 as Complete)
    - [x] Finalize `pr_description.md`
- [x] **PR Creation**
    - [x] `gh pr create` with detailed strategy description

