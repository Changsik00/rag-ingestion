# Task List: Spec 075

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Brain Layer Refactoring (Week 1)
### 3-1. Orchestration Components Structure
- [x] Create `app/application/rag/orchestration/` directory
- [x] Create `app/application/rag/orchestration/service.py` (Main Orchestrator)
- [x] Create `app/domain/rag/brain/answer_generator.py` (LLM Answer Logic)
- [x] Create `app/domain/rag/brain/reranker.py` (Reranking Logic)
- [x] Test: `tests/application/rag/orchestration/test_service.py`

### 3-2. Wiring Components & LangGraph Integration
- [x] Implement `RAGOrchestrator` class
- [x] Wiring: Brain -> Retrieval -> Brain (Rerank/Generate)
- [x] Port `generate_answer` logic to `AnswerGenerator`
- [x] Port `rerank` logic to `Reranker`
- [x] Unit Test passing (Mock ALL dependencies)
- [x] Commit: `refactor(spec-075): separate orchestration layer`

---

## Task 2: Retrieval Layer Refactoring (Week 2)
### 2-1. Retrieval Components Structure
- [x] Create `app/infrastructure/rag/retrieval/` directory
- [x] Create `app/infrastructure/rag/retrieval/service.py` (Hybrid Search logic)
- [x] Test: `tests/infrastructure/rag/retrieval/test_service.py`

### 2-2. Port Logic to Retrieval Service
- [x] Port `retrieve_hybrid` from `rag_nodes.py`
- [x] Port `_search_vector`, `_search_keyword`, `_search_graph` helpers
- [x] Port `rerank_results` logic (`_rerank_pointwise`, `_rerank_listwise`)
- [x] Unit Test passing (Mock DB Repos)
- [x] Commit: `refactor(spec-075): separate retrieval layer`

---

## Task 3: Orchestration Layer Refactoring (Week 3)
### 3-1. Orchestration Layer 구조 생성
- [ ] `app/application/rag/orchestration/` 디렉토리 생성
- [ ] `app/application/rag/orchestrator.py` 작성
- [ ] `BrainService` 및 `RetrievalService` 인터페이스 정의 및 주입

### 3-2. LangGraph 재구성 (Wiring)
- [ ] `RAGOrchestrator` 메서드를 사용하는 새로운 LangGraph 정의
- [ ] State 흐름 검증
- [ ] Integration Test 실행: 전체 흐름 연결 확인
- [ ] Commit: `refactor(spec-075): separate orchestration layer`

---

## Task 4: Integration & Cleanup (Week 4)
### 4-1. E2E 검증 (Verification)
- [ ] 전체 E2E 테스트 스위트 실행
- [ ] 채팅, 검색, 의도 분류 등 기존 기능 정상 동작 확인
- [ ] LangSmith 트레이스를 통한 노드 실행 검증

### 4-2. 정리 및 문서화 (Cleanup)
- [ ] `app/infrastructure/ai/rag_nodes.py` 파일 삭제
- [ ] 아키텍처 문서 (ADR) 업데이트
- [ ] `ruff check .` 실행으로 미사용 import 정리
- [ ] Final Commit: `chore(spec-075): cleanup deprecated rag_nodes.py`

## Summary
**총 Task**: 8 Step (4 Weeks)
**예상 커밋 수**: 10-15개
**현재 진행**: Planning
