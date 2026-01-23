# Spec 033: LangGraph State Management (Nervous System)

## 📋 배경 및 문제 정의 (Background & Problem)

### 현재 상황
**Spec 032**에서 `IntentClassifier`를 구현하여 사용자 의도를 분류하고, `RAGService`에서 Intent → Filters 변환을 수행하는 기능을 구현했습니다. 그러나 현재 시스템은 다음과 같은 구조적 한계가 있습니다:

1. **단순 함수 기반 처리**: RAG 파이프라인이 일반 Python 함수(`retrieve_and_generate()`)로 구현되어 있어, 의사결정 과정이 코드 내부에 숨겨져 있음
2. **암묵적 상태 전달**: Intent, Filters, Rewritten Query 등의 중간 결과가 지역 변수로만 관리되어 추적 불가능
3. **Ingestion vs RAG 불일치**: Ingestion 파이프라인은 LangGraph 기반이지만, RAG 파이프라인은 아직 전통적인 방식으로 구현됨
4. **디버깅 불가능**: 의사결정 흐름(Intent → Filters → Search)이 State로 저장되지 않아 Admin Dashboard에서 가시성 부족

### 문제점
**Design Guide 005**의 핵심 철학을 위반하고 있습니다:
- **Brain (LLM)**: Intent Classifier는 잘 작동하지만
- **Nervous System (LangGraph)**: 존재하지 않음 (단순 함수 호출)
- **Memory/Body (RAG System)**: Repository는 준비되었지만 State 기반 제어 없음

이로 인해:
- ❌ 의사결정 과정이 불투명함 (Black Box)
- ❌ HITL(Human-in-the-Loop) 적용 불가능 (Interrupt 지점 없음)
- ❌ 재실행 시 Context 유실 (Checkpointer 미적용)
- ❌ Spec 032의 Intent Classification이 단순 로깅으로만 활용됨

### 해결 방안
RAG 파이프라인을 **LangGraph 기반**으로 전환하여 3-Layer 아키텍처를 완성합니다:

| Layer | Component | 구현 방식 |
|:---:|:---:|:---|
| **Brain** | Intent Classifier, Query Rewriter | LLM을 사용한 의사결정 노드 (이미 구현됨) |
| **Nervous System** | LangGraph (`RAGGraphState`) | Router → Retrieval → Generator 흐름을 State 기반으로 제어 |
| **Memory/Body** | DocumentRepository, ChromaRepository | State의 `filters` 필드를 읽어 물리적 검색 범위 강제 |

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **RAGGraphState 정의**: LangGraph State 스키마 설계
   - `query`: 원본 사용자 질문
   - `rewritten_query`: Query Rewriter 결과
   - `user_intent`: Intent Classifier 결과 (`UserIntent` Pydantic 모델)
   - `filters`: Repository에 전달할 필터 (dict)
   - `vector_chunks`, `keyword_chunks`, `graph_data`: 검색 결과
   - `final_answer`: 생성된 답변

2. **RAG Graph 구성**: 4개 노드로 파이프라인 구성
   - `classify_intent`: Intent Classification + Query Rewriting
   - `route_decision`: Intent → Filters 변환 (Deterministic Logic)
   - `retrieve_hybrid`: Parallel Hybrid Search (Vector + Keyword + Graph)
   - `generate_answer`: LLM을 사용한 답변 생성

3. **RAGService 리팩토링**: LangGraph 기반으로 전환
   - 기존 `retrieve_and_generate()` → Graph Invocation으로 대체
   - State 기반 데이터 전달로 변경

4. **Checkpointer 통합**: SQLite Checkpointer 적용
   - State Snapshot 저장 (HITL 준비)
   - Thread ID 기반 State 조회 가능

### Non-Functional Requirements
1. **성능**: 기존 대비 Latency +50ms 이하 (Graph Overhead)
2. **호환성**: 기존 API Signature 유지 (Breaking Change 없음)
3. **가시성**: Admin Dashboard에서 Graph State 조회 가능
4. **테스트 가능성**: 각 노드를 독립적으로 단위 테스트 가능

## ✅ Definition of Done
1. `RAGGraphState` (TypedDict) 정의 및 Graph 구성 완료
2. `RAGService`가 LangGraph 기반으로 동작하며 모든 Integration Test 통과
3. Admin Dashboard에서 State Snapshot 조회 가능
4. 전체 테스트 스위트 통과 (`pytest` + `ruff check`)
5. Documentation 업데이트 (`docs/architecture/rag_pipeline.md` 신규 작성)
