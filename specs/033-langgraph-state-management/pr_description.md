# feat(spec-033): langgraph state management for rag pipeline

## 📋 Summary

기존 함수 기반 RAG 파이프라인을 **LangGraph 기반**으로 전환하여 의사결정 과정을 State로 명시적으로 관리합니다.

**Before**: 단순 Python 함수로 구현된 RAG Service (Intent → Filters 변환이 암묵적)
**After**: LangGraph 기반 4-Node Pipeline (모든 중간 상태가 RAGGraphState에 저장)

**Design Guide 005**의 3-Layer 아키텍처를 완성:
- **Brain** (LLM): Intent Classification, Query Rewriting
- **Nervous System** (LangGraph):  State 기반 흐름 제어
- **Memory/Body** (Repository): 물리적 검색 및 필터 강제

## 🎯 Key Review Points

1. **RAGGraphState 스키마 설계**: 모든 중간 상태(Intent, Filters, 검색 결과)를 TypedDict로 관리
2. **RAGNodes 비즈니스 로직**: 4개 노드(classify_intent, route_decision, retrieve_hybrid, generate_answer)가 State를 업데이트
3. **RAGService API 호환성**: 기존 `retrieve_and_generate()` 인터페이스는 유지하되 내부 구현만 변경

## 🧪 Verification

### Automated Tests
```bash
# Unit Tests (RAG Nodes)
uv run pytest tests/unit/infrastructure/rag/ -v
# 결과: 5 passed

# Integration Tests (RAG Graph Flow)
uv run pytest tests/integration/bdd/test_rag_graph_flow.py -v
# 결과: 3 skipped (실제 LLM 연동 후 활성화)
```

### Manual Verification
```bash
# Streamlit Admin UI에서 RAG Playground 테스트
uv run streamlit run app/admin/app.py
```

## 📦 Files Changed

### 🆕 New Files
- `app/domain/rag/state.py`: RAGGraphState TypedDict 정의
- `app/infrastructure/rag/nodes.py`: RAGNodes 클래스 (4개 노드 비즈니스 로직)
- `app/infrastructure/rag/graph.py`: RAGGraphBuilder 클래스 (Graph 구성 및 컴파일)
- `tests/unit/infrastructure/rag/test_rag_nodes.py`: RAG Nodes 단위 테스트 (5개 시나리오)
- `tests/integration/bdd/test_rag_graph_flow.py`: RAG Graph E2E 테스트 (3개 시나리오)
- `docs/architecture/rag_pipeline.md`: RAG Pipeline 구조 문서

### 🛠 Modified Files
- `app/domain/services/rag_service.py` (+108, -170): 함수 기반 → Graph 기반으로 완전 리팩토링
- `app/interfaces/api/dependencies.py` (+28, -9): RAG Graph Components DI 추가
- `backlog/queue.md` (+1, -0): Spec 033 Note 추가

**Total:** 12 files changed, 9 new, 3 modified

## ✅ Definition of Done
- [x] `RAGGraphState` TypedDict 정의 완료
- [x] RAG Graph (4-Node Pipeline) 구성 완료
- [x] `RAGService` LangGraph 기반으로 전환 완료
- [x] Unit Tests 통과 (5 passed)
- [x] Integration Tests 작성 (3 skipped - 실제 LLM 연동 후 활성화)
- [x] Checkpointer 통합 완료 (HITL 준비)
- [x] Documentation 업데이트 완료 (`docs/architecture/rag_pipeline.md`)
