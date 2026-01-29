# Implementation Plan: Spec 032 - Router & Intent Classifier

## 📋 Branch Strategy
- `feature/032-router-intent-classifier`

## 🛑 User Review Required

> [!WARNING]
> **LLM 비용 증가**: 모든 RAG 쿼리에서 Intent Classification 단계가 추가되므로 LLM 호출 1회 증가 (약 +200ms, +$0.001/query)

> [!IMPORTANT]
> **Fallback Strategy**: Intent Classifier가 실패하거나 타임아웃 시 일반 검색(General Query)으로 Fallback하여 서비스 중단 방지

**검토 필요 사항:**
- [x] Intent Classification 호출 비용 증가 허용 여부
- [x] Fallback 전략 (파싱 실패 시 전체 검색) 동의 여부

## 🎯 Core Strategy

### 1. 아키텍처 설계 (3-Layer Pattern)
**Design Guide 005**의 철학을 준수하여 다음과 같이 구현합니다:

| Layer | Component | Responsibility |
|:---:|:---:|:---|
| **Brain** | `IntentClassifier` (Domain Service) | LLM을 사용하여 사용자 의도 분석 및 구조화된 결정 반환 |
| **Nervous System** | `RAGService` (Orchestrator) | Classifier 결과를 Filters로 변환하여 Repository 전달 |
| **Body** | `DocumentRepository` (Infrastructure) | 물리적 검색 범위 강제 (이미 Spec 031에서 구현됨) |

### 2. Intent Schema 설계
**Pydantic 모델**을 사용하여 LLM 출력을 구조화하고 검증합니다:

```python
# app/domain/schemas/intent.py
from enum import Enum
from pydantic import BaseModel, Field

class IntentType(str, Enum):
    GENERAL_QUERY = "general_query"  # 전체 검색
    COMPARE = "compare"  # 특정 문서 비교
    SUMMARIZE = "summarize"  # 특정 문서 요약
    FILTER_BY_TOPIC = "filter_by_topic"  # 주제별 필터링

class UserIntent(BaseModel):
    intent: IntentType
    targets: list[str] = Field(default_factory=list, description="Document IDs, URLs, or Entity Names")
    reasoning: str = Field(description="Why this intent was chosen (for debugging)")
```

### 3. Prompt Engineering
QueryRewriter와 유사한 패턴으로 Intent Classification을 수행합니다:

```
You are an expert intent classifier for a RAG system.
Analyze the user query and return a structured JSON with:
- intent: one of [general_query, compare, summarize, filter_by_topic]
- targets: list of specific document identifiers (if any)
- reasoning: brief explanation of your decision

Examples:
User: "Claude와 GPT-4를 비교해줘"
→ {"intent": "compare", "targets": ["claude", "gpt-4"], "reasoning": "User wants comparison"}

User: "인공지능이 뭐야?"
→ {"intent": "general_query", "targets": [], "reasoning": "No specific target mentioned"}
```

### 4. RAGService 통합 전략
**기존 코드** (`app/domain/services/rag_service.py`):
```python
async def retrieve_and_generate(self, query: str, history: list[dict], filters: dict | None = None) -> RAGResult:
    rewritten_query = self.query_rewriter.rewrite(query, history)
    # ... 검색 로직
```

**변경 후**:
```python
async def retrieve_and_generate(self, query: str, history: list[dict], filters: dict | None = None) -> RAGResult:
    # 1. Query Rewriting
    rewritten_query = self.query_rewriter.rewrite(query, history)
    
    # 2. Intent Classification (신규)
    user_intent = self.intent_classifier.classify(query, history)
    
    # 3. Convert Intent to Filters
    derived_filters = self._intent_to_filters(user_intent)
    
    # 4. Merge with Manual Filters (Manual > Auto)
    final_filters = filters or derived_filters
    
    # 5. Hybrid Search (기존 로직)
    # ... (unchanged)
```

### 5. Graceful Degradation
LLM 파싱 실패 시 안전한 Fallback:
```python
try:
    user_intent = self.intent_classifier.classify(query, history)
except (ValidationError, TimeoutError) as e:
    logger.warning(f"Intent classification failed: {e}. Falling back to general search.")
    user_intent = UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="Fallback")
```

---

## 📂 Proposed Changes

### Domain Layer

#### [NEW] `app/domain/schemas/intent.py`
Intent 분류 결과를 위한 Pydantic Schema 정의.

```python
from enum import Enum
from pydantic import BaseModel, Field

class IntentType(str, Enum):
    GENERAL_QUERY = "general_query"
    COMPARE = "compare"
    SUMMARIZE = "summarize"
    FILTER_BY_TOPIC = "filter_by_topic"

class UserIntent(BaseModel):
    intent: IntentType
    targets: list[str] = Field(default_factory=list)
    reasoning: str
```

#### [NEW] `app/domain/services/intent_classifier.py`
LLM을 사용하여 사용자 쿼리의 의도를 분석하는 Domain Service.

**핵심 메서드**:
- `classify(query: str, history: list[dict]) -> UserIntent`
- LLM Prompt 구성 → JSON 파싱 → Pydantic 검증

**참고**: `QueryRewriter`와 동일한 패턴 사용 (히스토리 제한, 예외 처리, Fallback)

---

#### [MODIFY] `app/domain/services/rag_service.py`
`RAGService`에 Intent Classifier 통합.

**변경 사항**:
1. Constructor에 `intent_classifier: IntentClassifier` 추가
2. `retrieve_and_generate()` 메서드에 Intent 분류 단계 추가
3. `_intent_to_filters()` 헬퍼 메서드 추가

```python
def _intent_to_filters(self, intent: UserIntent) -> dict | None:
    if intent.intent == IntentType.COMPARE or intent.intent == IntentType.SUMMARIZE:
        # targets를 document_id 필터로 변환
        return {"document_id": intent.targets} if intent.targets else None
    elif intent.intent == IntentType.FILTER_BY_TOPIC:
        # targets를 topic/entity 필터로 변환
        return {"topic": intent.targets} if intent.targets else None
    else:
        return None  # GENERAL_QUERY
```

---

### Infrastructure Layer

#### [MODIFY] `app/interfaces/api/dependencies.py`
Dependency Injection 설정에 `IntentClassifier` 추가.

```python
def get_intent_classifier(llm: LLMInterface = Depends(get_llm)) -> IntentClassifier:
    return IntentClassifier(llm)

def get_rag_service(
    neo4j_doc_repo=Depends(...),
    neo4j_graph_repo=Depends(...),
    chroma_repo=Depends(...),
    query_rewriter=Depends(get_query_rewriter),
    intent_classifier=Depends(get_intent_classifier),  # 신규
    llm=Depends(get_llm)
) -> RAGService:
    return RAGService(...)
```

---

### Admin Layer

#### [MODIFY] `app/admin/pages/4_RAG_Playground.py`
Intent Classification 결과를 Debug View에 표시.

**추가 UI**:
- Expander: "🧠 Intent Analysis"
  - Intent Type Badge
  - Targets List
  - Reasoning Explanation

```python
with st.expander("🧠 Intent Analysis"):
    st.badge(result.intent.value)
    st.write("**Targets:**", result.targets)
    st.caption(result.reasoning)
```

---

### Test Layer

#### [NEW] `tests/unit/domain/services/test_intent_classifier.py`
Mock LLM을 사용한 Intent Classifier 단위 테스트.

**테스트 시나리오**:
1. 비교 의도 감지 ("A와 B를 비교해줘")
2. 요약 의도 감지 ("이 문서 요약해줘")
3. 일반 쿼리 처리 ("인공지능이 뭐야?")
4. LLM 응답 파싱 실패 시 예외 처리
5. Pydantic 검증 실패 시 Fallback

---

#### [NEW] `tests/integration/bdd/test_intent_routing.py`
실제 LLM을 사용한 End-to-End Intent Routing 테스트.

**Given-When-Then 시나리오**:

**Scenario 1: 비교 의도 자동 감지**
- Given: 지식 베이스에 "Claude" 문서와 "GPT-4" 문서가 존재
- When: 사용자가 "Claude와 GPT-4를 비교해줘" 요청
- Then: Intent = COMPARE, Targets = ["claude", "gpt-4"], 두 문서만 검색됨

**Scenario 2: Fallback to General Query**
- Given: LLM이 잘못된 JSON 반환
- When: Intent Classification 실패
- Then: GENERAL_QUERY로 Fallback하여 전체 검색 수행

---

## 🧪 Verification Plan

### Automated Tests

#### Unit Tests
```bash
# Intent Classifier Logic (Mocked LLM)
uv run pytest tests/unit/domain/services/test_intent_classifier.py -v
```

**검증 항목**:
- ✅ 4가지 Intent Type 모두 정확히 분류
- ✅ Pydantic Schema 검증 통과
- ✅ LLM 파싱 실패 시 예외 처리

---

#### Integration Tests
```bash
# End-to-End Intent Routing (Real LLM)
uv run pytest tests/integration/bdd/test_intent_routing.py -v
```

**검증 항목**:
- ✅ 실제 Gemini LLM으로 Intent 분류 성공
- ✅ Intent → Filters 변환 정확성
- ✅ RAGService 통합 동작 확인

---

#### Full Test Suite
```bash
# 모든 테스트 통과 확인
uv run pytest -v
```

---

### Manual Verification

#### 1. Admin Dashboard에서 Intent Debug View 확인
1. Streamlit Admin 실행: `uv run streamlit run app/admin/app.py`
2. "RAG Playground" 페이지 이동
3. 다음 쿼리 입력 후 Intent Analysis Expander 확인:
   - "Claude와 GPT-4를 비교해줘" → Intent: `COMPARE`, Targets: `["claude", "gpt-4"]`
   - "인공지능이 뭐야?" → Intent: `GENERAL_QUERY`, Targets: `[]`

#### 2. Latency 측정
- Before: RAG 파이프라인 평균 응답 시간 측정 (베이스라인)
- After: Intent Classification 추가 후 응답 시간 측정
- **목표**: +200ms 이하 증가 확인

---

## 📊 Expected Impact

### Performance
- **Latency**: +150~200ms (LLM 호출 1회 추가)
- **Token Usage**: +200 tokens per query (Intent Classification Prompt)

### Quality
- **Precision**: 특정 문서 비교/요약 시 불필요한 검색 제거 → Hallucination 감소
- **User Experience**: 자연어로 의도를 표현해도 시스템이 정확히 이해

### Maintainability
- **Testability**: Mock LLM으로 Intent Logic 독립 테스트 가능
- **Observability**: Admin Dashboard에서 Intent 결정 과정 가시화
