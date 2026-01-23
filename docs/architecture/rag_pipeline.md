# RAG Pipeline Architecture

## 개요
RAG (Retrieval-Augmented Generation) 파이프라인은 **LangGraph 기반**으로 구현되어 있으며, 사용자 질문에 대해 관련 지식을 검색하고 답변을 생성합니다.

**Spec 033: LangGraph State Management**에서 기존 함수 기반 로직을 Graph 기반으로 전환하여 의사결정 과정을 State로 명시적으로 관리합니다.

## 아키텍처 (Design Guide 005: 3-Layer Pattern)

```mermaid
graph TB
    A[User Query] --> B[classify_intent]
    B --> C[route_decision]
    C --> D[retrieve_hybrid]
    D --> E[generate_answer]
    E --> F[Final Answer]
    
    B -.Brain Layer.-> B
    C -.Nervous System.-> C
    D -.Memory/Body.-> D
```

### 레이어 구조

| Layer | Component | Responsibility |
|:---:|:---:|:---|
| **Brain** | Intent Classifier, Query Rewriter | LLM을 사용한 의사결정 (Intent Classification, Query Rewriting) |
| **Nervous System** | LangGraph (RAGGraphState) | State 기반 흐름 제어 및 데이터 전달 |
| **Memory/Body** | Document Repository, Graph Repository | 물리적 검색 및 필터 강제 실행 |

## RAGGraphState 스키마

모든 중간 상태를 명시적으로 관리하는 TypedDict:

```python
class RAGGraphState(TypedDict):
    # Input
    query: str
    history: list[dict]
    manual_filters: dict | None
    
    # Brain (LLM Decisions)
    user_intent: UserIntent | None
    rewritten_query: str | None
    
    # Nervous System (Routing)
    auto_filters: dict | None
    final_filters: dict | None
    
    # Body (Results)
    vector_chunks: list[Chunk]
    keyword_chunks: list[Chunk]
    graph_data: list[dict]
    
    # Output
    full_context: str
    final_answer: str
```

## Graph 플로우

### Node 1: classify_intent
- **역할**: Intent Classification + Query Rewriting
- **Input**: `query`, `history`
- **Output**: `user_intent`, `rewritten_query`

### Node 2: route_decision
- **역할**: Intent → Filters 변환
- **Input**: `user_intent`, `manual_filters`
- **Output**: `auto_filters`, `final_filters`
- **로직**: `COMPARE`/`SUMMARIZE` 등에서 타겟을 `source` 필터로 변환. Manual Filters 우선.

### Node 3: retrieve_hybrid
- **역할**: Parallel Hybrid Search (Vector + Keyword + Graph)
- **주요 특징**: `asyncio.to_thread`를 사용하여 동기 DB 리포지토리를 병렬로 실행.

### Node 4: generate_answer
- **역할**: Context Formatting + LLM Generation
- **로직**: 검색된 청크들에 Citations(출처)를 부여하여 컨텍스트 생성 후 LLM 호출.

---

## ⚠️ Troubleshooting & Lessons Learned (Spec 033 Review)

테스트 및 리뷰 과정에서 발견된 주요 이슈와 이에 대한 상세 원인 분석 기록입니다.

### 1. 필터링 강도와 데이터 불일치 이슈 (Scenario 2: Strict Filtering)

**현상 및 제보 내용**:
- "Claude와 GPT-4 비교", "일론 머스크와 스티브 잡스의 공통점" 등 특정 대상을 지목한 질문 시 검색 결과가 0건(`Document Context: [EMPTY]`)으로 나타남.

**상세 원인 분석**:
- **Intent Classifier의 동작**: `Intent: COMPARE`, `Targets: ["일론 머스크", "스티브 잡스"]`로 의도를 아주 정확하게 파악함.
- **Strict Filtering의 함정**: 파이프라인은 추출된 타겟을 바탕으로 `source` 필드 필터링을 강제함. 
  - 검색 명령: `source가 ["일론 머스크", "스티브 잡스"]인 문서를 찾아라.`
  - 실제 DB 상태: 문서는 `Elon Musk Bio`라는 영어 타이틀/소스로 저장되어 있거나, `tech_wiki`와 같은 다른 소스 명칭을 가짐.
- **결과**: 한글 대상명과 실제 DB의 소스 명칭이 **정확히 일치(Exact Match)**하지 않아 필터링 단계에서 모든 검색 결과가 차단됨.

---

### 2. Context 부재 시 LLM의 자의적 답변 (Hallucination 위험)

**현상 및 제보 내용**:
- "일론 머스크와 스티브 잡스의 공통점" 질문 시, 분명히 `Document Context`는 비어있음에도 불구하고 LLM이 "혁신적인 비전, 강력한 리더십..." 등 매우 훌륭한 답변을 내놓음.

**상세 원인 분석**:
- **RAG의 기본 전제**: RAG는 주어진 Context 내에서만 답을 찾아야 함.
- **프롬프트 제어 부족**: 현재 `nodes.py`의 `generate_answer` 노드에 설정된 프롬프트가 충분히 엄격하지 않음. 
  - "컨텍스트 기반으로 답해라"라는 지시는 있으나, **"컨텍스트에 정보가 아예 없으면 절대 지어내지 말고 모른다고 답해라"**라는 강력한 제약(Guardrail)이 부족함.
- **결과**: LLM이 자신의 내부 지식(Internal Knowledge)을 동원하여 답변함으로써, 사용자는 시스템이 DB 정보를 사용한 것으로 오해할 수 있는 상황이 발생함.

---

### 개선 방향 (Spec 034 이관)
- **Fallback 검색 로직**: 필터 검색 결과가 0건일 경우, 자동으로 필터를 해제하고 전체 검색(Global Search)을 수행하여 의미적으로 유사한 문서를 다시 찾는 시퀀스 추가.
- **프롬프트 강화 (Empty Guard)**: Context가 비어있거나 불충분할 경우 반드시 지식 부족을 시인하도록 프롬프트 엔지니어링 수행.

---

## Checkpointer 통합
`SqliteSaver`를 사용하여 State Snapshot을 저장하며, 이를 통해 Admin Dashboard에서 과거의 의사결정 과정을 추적할 수 있습니다.
