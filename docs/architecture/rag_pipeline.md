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
- **결과**: 한글 대상명과 실제 DB의 소스 명칭이 **정확히 일치(Exact Match)**하지 않아 필터링 단계에서 모든 검색 결과가 차단됨.

**해결 (Spec 034)**:
- **Filter Fallback 로직 도입**: 필터링된 검색 결과가 0건일 경우, 자동으로 필터를 해제하고 **전역 검색(Global Search)**을 재수행하여 최소한의 컨텍스트를 확보함.
- `fallback_triggered` 상태를 통해 사용자에게 전역 검색 결과임을 고지함.

---

### 2. Context 부재 시 LLM의 자의적 답변 (Hallucination 위험)

**현상 및 제보 내용**:
- "일론 머스크와 스티브 잡스의 공통점" 질문 시, 분명히 `Document Context`는 비어있음에도 불구하고 LLM이 "혁신적인 비전, 강력한 리더십..." 등 매우 훌륭한 답변을 내놓음.

**상세 원인 분석**:
- **RAG의 기본 전제**: RAG는 주어진 Context 내에서만 답을 찾아야 함.
- **결과**: LLM이 자신의 내부 지식(Internal Knowledge)을 동원하여 답변함으로써, 사용자는 시스템이 DB 정보를 사용한 것으로 오해할 수 있는 상황이 발생함.

**해결 (Spec 034)**:
- **Negative Constraints 강화**: 프롬프트에 "컨텍스트에 정보가 부족하면 명확히 모른다고 답하라"는 **CRITICAL RULES**를 추가하여 내부 지식 사용을 엄격히 제한함.

---

### 3. Manual Filter와 의도 사이의 충돌 (Scenario 3: Manual Override)

**현상 및 제보 내용**:
- 사용자가 UI에서 특정 문서(예: "일론 머스크")를 고정(Manual Filter)한 후 무거운 비교 질문을 던졌으나, 필터에 의해 다른 정보(스티브 잡스)가 차단되어 답변 품질이 저하됨.
- 제보 요지: "Search Documents 부분이 1개만 선택되는 것(혹은 하나만 고정하는 것)이 의도적인 비교 시나리오를 방해할 수 있다."

**상세 원인 분석**:
- **필터 배타성**: 현재 로직은 사용자 수동 필터를 최우선 시함. 사용자가 "머스크"만 고정하면 시스템은 "잡스" 정보가 DB에 있어도 절대 보지 않음.
- **데이터 파편화**: 특정 문서 내의 정보가 가십성(트윗 등)인 경우, '비교'라는 복합적인 Intent를 처리하기에 부적절한 Context가 되어 답변이 어색해짐.

**설계 고민 및 개선 방향 (Spec 034+)**:
- **UI/UX 조율**: 수동 필터가 걸려 있더라도 Intent 달성을 위해 추가 정보가 필요한 경우, 사용자에게 필터 해제를 제안하거나 동적으로 범위를 확장하는 지능형 검색 전환 필요.

---

## 🏗️ RAG Evolution: From Strict to Hybrid

Spec 033/034 개발 과정에서 "Strict RAG(제시된 컨텍스트 내에서만 답변)"의 한계가 명확히 드러났습니다. 이에 따라 시스템의 철학을 **Flexible Hybrid Knowledge Strategy**로 확장합니다.

### 1. The "Strict RAG" Problem (Spec 033 Findings)
- **과도한 배타성**: 사용자가 의도한 대상(예: "잡스")이 DB에 있더라도 필터 명칭 불일치로 인해 차단되는 현상 발생.
- **사용자 경험 저하**: DB에 정보가 부족할 때 LLM이 충분히 답할 수 있는 상식임에도 불구하고 "모른다"고 답변하여 도구로서의 가치가 하락함.

### 2. The "Flexible RAG" Strategy (Spec 034+)
- **Adaptive Retrieval**: 필터 결과가 없을 경우 자동으로 Global Search로 전환 (이미 구현).
- **Graceful Collaboration**: DB 정보와 LLM 지식을 융합하되, 그 경계를 투명하게 공개.

### 3. Future Vision (Spec 035+)
- **Citations First**: 답변 내에 `[1]` 등의 인덱스를 사용하여 DB 근거와 LLM 보충 지식을 시각적으로 구분.
- **Intent-based Balancing**: 질문의 성격에 따라 RAG 의존도(Strictness Level)를 동적으로 조절.

---

## Checkpointer 통합 및 상태 관리
`SqliteSaver`를 사용하여 State Snapshot을 저장하며, 이를 통해 Admin Dashboard에서 과거의 의사결정 과정을 추적할 수 있습니다.

### Troubleshooting: `checkpoints.sqlite` 손상 및 Playground 미연동 이슈 (2026-01-24)
- **현상**: `sqlite3.DatabaseError: file is not a database` 발생.
- **원인**: `checkpoints.sqlite` 파일이 알 수 없는 바이너리 데이터(UUID 등 포함)로 채워져 SQLite 형식이 파괴됨. 또한 `4_RAG_Playground.py`에서 `graph_builder.build()` 호출 시 `checkpointer` 인자가 누락되어 Playground 대화 내역이 저장되지 않는 문제 발견.
- **해결 및 후속 조치**:
  1. 손상된 파일을 백업하고 정상적인 SQLite DB로 교체 완료.
  2. `rag-backend` 컨테이너에는 `sqlite3` CLI가 없으므로 Python 스크립트(`check_states.py`)를 통해 관리하도록 프로세스 정립.
  3. Spec 034 작업 시 Playground 코드에 `checkpointer`를 명시적으로 주입하도록 수정 예정.
