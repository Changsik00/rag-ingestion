# feat(spec-032): router and intent classifier

## 📋 개요

LLM 기반 Intent Classification을 추가하여 사용자 질문의 의도를 자동 파악하고, RAG 검색 필터를 지능적으로 적용합니다.

## 🎯 주요 변경사항

### 1. Intent Classifier Domain Service
- **Schema 정의** (`app/domain/schemas/intent.py`)
  - `IntentType` Enum: GENERAL_QUERY, COMPARE, SUMMARIZE, FILTER_BY_TOPIC
  - `UserIntent` Pydantic Model: intent, targets, reasoning

- **Service 구현** (`app/domain/services/intent_classifier.py`)
  - LLM Prompt Engineering으로 의도 분류
  - JSON 파싱 및 Pydantic 검증
  - 에러 처리 (JSONDecodeError → ValueError)

### 2. RAG Service 통합
- **RAGService 확장** (`app/domain/services/rag_service.py`)
  - Intent Classification 단계 추가
  - `_classify_intent_with_fallback()`: Graceful Degradation 전략
  - `_intent_to_filters()`: Intent를 Repository 필터로 자동 변환
  - Manual 필터 우선 (User Override 지원)

- **RAGResult 확장**
  - `user_intent: UserIntent | None` 필드 추가

- **Dependency Injection** (`app/interfaces/api/dependencies.py`)
  - `get_intent_classifier()` 추가
  - `get_rag_service()`에 intent_classifier 주입

### 3. Admin Dashboard Debug View
- **UI 업데이트** (`app/admin/pages/4_RAG_Playground.py`)
  - IntentClassifier dependency 추가
  - Intent Analysis Expander 추가 (Intent Type, Targets, Reasoning 표시)

- **Admin Agent 통합** (`app/admin/agents/admin_agent.py`)
  - `search_node()`에서 `user_intent` context_data에 포함

## 🧪 테스트

### Unit Tests
- `tests/unit/domain/test_intent_classifier.py` (7개 시나리오)
  - ✅ General Query 분류
  - ✅ Compare Intent 분류
  - ✅ Summarize Intent 분류
  - ✅ Filter by Topic 분류
  - ✅ Invalid JSON → ValueError
  - ✅ Invalid Intent Type → ValidationError
  - ✅ History Context 포함 확인

### Integration Tests
- `tests/integration/bdd/test_intent_routing.py` (5개 BDD 시나리오)
  - 실제 LLM 사용 (환경 의존적)
  - Fixture 기반 LLM Adapter 주입

### 검증 결과
```bash
uv run pytest tests/unit/domain/test_intent_classifier.py -v
# ================================== 7 passed in 0.06s ===================================
```

## 📊 파일 변경 내역

### 신규 파일
- `app/domain/schemas/intent.py` - Intent Schema 정의
- `app/domain/services/intent_classifier.py` - Intent Classifier Service 구현
- `tests/unit/domain/test_intent_classifier.py` - Unit Test 7개
- `tests/integration/bdd/test_intent_routing.py` - Integration Test 5개
- `specs/032-router-intent-classifier/spec.md` - Spec 문서
- `specs/032-router-intent-classifier/plan.md` - 구현 계획
- `specs/032-router-intent-classifier/task.md` - 작업 체크리스트
- `specs/032-router-intent-classifier/walkthrough.md` - 구현 Walkthrough

### 수정 파일
- `app/domain/services/rag_service.py` - Intent Classification 단계 추가, RAGResult 확장
- `app/interfaces/api/dependencies.py` - Intent Classifier DI 설정
- `app/admin/pages/4_RAG_Playground.py` - Intent Debug View 추가
- `app/admin/agents/admin_agent.py` - context_data에 user_intent 포함

## 💡 핵심 개선사항

### 1. 자동 필터링
- "Claude와 GPT-4를 비교해줘" → 자동으로 두 문서만 검색
- "Python 관련된 것만 보여줘" → `topic='Python'` 필터 자동 적용

### 2. Graceful Degradation
- LLM 파싱 실패 시 GENERAL_QUERY Fallback
- 시스템 안정성 보장

### 3. 디버깅 지원
- Admin Dashboard에서 Intent 분류 결과 실시간 확인
- Reasoning 필드로 LLM 결정 근거 파악

## 🔗 관련 문서

- [Design Guide 005: LLM RAG Strategy](../docs/design_guides/005-llm-rag-strategy.md)
- [Spec 032: Router & Intent Classifier](specs/032-router-intent-classifier/spec.md)
- [Walkthrough](specs/032-router-intent-classifier/walkthrough.md)

## 📝 커밋 히스토리

```
969b89a feat(spec-032): add intent routing debug view to admin dashboard
50c763a style(spec-032): apply ruff formatting and fix lint errors
d0090e2 feat(spec-032): integrate intent classifier into rag service
fcb8af8 test(spec-032): add intent routing integration tests
a48cb94 test(spec-032): add intent classifier test cases
```

## ✅ Definition of Done

- [x] Intent Classifier Domain Service 구현
- [x] RAG Service 통합
- [x] Admin Dashboard Debug View 추가
- [x] Unit Test 7개 작성 (모두 통과)
- [x] Integration Test 5개 작성
- [x] Lint \u0026 Format 적용
- [x] Walkthrough 문서 작성
- [x] PR Description 작성
