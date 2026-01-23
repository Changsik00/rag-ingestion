# Walkthrough: Spec 032 - Router & Intent Classifier

## 📋 목표

LLM을 활용하여 사용자의 의도를 자동으로 파악하고, RAG 검색 시 적절한 필터를 자동으로 생성하는 Intent Classifier를 구현합니다.

## ✅ 구현 내역

### 1. Intent Classifier Domain Service

#### Schema 정의 (`app/domain/schemas/intent.py`)
```python
class IntentType(str, Enum):
    GENERAL_QUERY = "general_query"      # 일반 질문
    COMPARE = "compare"                   # 비교 요청
    SUMMARIZE = "summarize"               # 요약 요청
    FILTER_BY_TOPIC = "filter_by_topic"  # 주제 필터링

class UserIntent(BaseModel):
    intent: IntentType
    targets: list[str]  # 검색 대상 (문서 ID, URL, 엔티티 등)
    reasoning: str      # 분류 근거 (디버깅용)
```

#### Service 구현 (`app/domain/services/intent_classifier.py`)
- **LLM Prompt Engineering**: 사용자 쿼리와 히스토리를 분석하여 의도를 파악하는 상세한 프롬프트 설계
- **JSON Parsing**: LLM 응답에서 JSON 추출 및 Pydantic 검증
- **Error Handling**: JSON 파싱 실패 시 ValueError 발생, Caller가 Fallback 처리

**핵심 로직:**
```python
def classify(self, query: str, history: list[dict]) -> UserIntent:
    # 1. Prompt 생성 (Query + History)
    # 2. LLM 호출
    # 3. JSON 추출 및 Pydantic 검증
    # 4. UserIntent 반환
```

### 2. RAG Service 통합

#### RAGService 확장 (`app/domain/services/rag_service.py`)
```python
async def retrieve_and_generate(...):
    # 1. Intent Classification (NEW in Spec 032)
    user_intent = self._classify_intent_with_fallback(query, history)
    
    # 2. Convert Intent to Filters
    auto_filters = self._intent_to_filters(user_intent)
    
    # 3. Merge Filters (Manual override)
    final_filters = filters if filters else auto_filters
    
    # 4. Rewrite Query
    # 5. Hybrid Search (with filters)
    # 6. Generate Answer
```

**Graceful Fallback 전략:**
```python
def _classify_intent_with_fallback(self, query, history) -> UserIntent:
    try:
        return self.intent_classifier.classify(query, history)
    except Exception as e:
        logger.warning(f"Intent classification failed: {e}")
        return UserIntent(
            intent=IntentType.GENERAL_QUERY,
            targets=[],
            reasoning="Fallback due to classification error"
        )
```

**Intent → Filters 변환:**
- `COMPARE` / `SUMMARIZE`: targets를 `source` 필터로 변환
- `FILTER_BY_TOPIC`: targets를 `topic` 필터로 변환
- `GENERAL_QUERY`: 필터 없음 (전체 검색)

#### Dependency Injection (`app/interfaces/api/dependencies.py`)
```python
@lru_cache
def get_intent_classifier() -> IntentClassifier:
    llm_adapter = get_llm()
    return IntentClassifier(llm_adapter)

def get_rag_service(..., intent_classifier: IntentClassifier, ...):
    return RAGService(..., intent_classifier=intent_classifier, ...)
```

### 3. Admin Dashboard Debug View

#### RAGResult 확장
```python
@dataclass
class RAGResult:
    ...
    user_intent: UserIntent | None = None  # Spec 032
```

#### Streamlit UI (`app/admin/pages/4_RAG_Playground.py`)
- **Intent Analysis Expander** 추가
- Intent Type, Targets, Reasoning 표시
- **색상 코딩**: 각 Intent별 이모지 (🟢 General, 🔵 Compare, 🟡 Summarize, 🟣 Topic)

## 🧪 테스트

### Unit Tests (`tests/unit/domain/test_intent_classifier.py`)
7개 시나리오 작성 및 **모두 통과**:
1. ✅ General Query 분류
2. ✅ Compare Intent 분류
3. ✅ Summarize Intent 분류
4. ✅ Filter by Topic 분류
5. ✅ Invalid JSON → ValueError
6. ✅ Invalid Intent Type → ValidationError
7. ✅ History Context 포함 확인

### Integration Tests (`tests/integration/bdd/test_intent_routing.py`)
5개 BDD 시나리오 작성 (실제 LLM 사용, 환경 의존):
1. 비교 의도 명확한 쿼리
2. 일반 질문
3. History 기반 문맥 이해
4. 대명사 사용한 요약 요청
5. 주제 필터링

## 📊 검증 결과

### Unit Test
```bash
uv run pytest tests/unit/domain/test_intent_classifier.py -v
# 7 passed in 0.06s
```

### Code Quality
```bash
uv run ruff check . --fix
uv run ruff format .
# All formatting applied
```

## 🎯 핵심 개선사항

### 1. LLM 기반 자동 필터링
- 사용자가 "Claude와 GPT-4를 비교해줘" → 자동으로 두 문서만 검색
- "Python 관련된 것만 보여줘" → topic='Python' 필터 자동 적용

### 2. Graceful Degradation
- LLM 파싱 실패 시에도 시스템이 안정적으로 동작
- GENERAL_QUERY Fallback으로 전체 검색 수행

### 3. 디버깅 가능성
- Admin Dashboard에서 Intent 분류 결과 실시간 확인
- Reasoning 필드로 LLM 결정 근거 파악 가능

## 📝 커밋 히스토리

```
969b89a feat(spec-032): add intent routing debug view to admin dashboard
50c763a style(spec-032): apply ruff formatting and fix lint errors
d0090e2 feat(spec-032): integrate intent classifier into rag service
fcb8af8 test(spec-032): add intent routing integration tests
a48cb94 test(spec-032): add intent classifier test cases
```

## 🚀 다음 단계

- [ ] PR Merge 후 Production 배포
- [ ] 실사용 데이터로 Intent 분류 정확도 모니터링
- [ ] Intent Type 추가 (e.g., RECENT_ONLY, EXCLUDE, etc.)
- [ ] Multi-target 지원 개선
