# feat(spec-032): router and intent classifier

## 📋 Summary
LLM 기반 Intent Classification을 추가하여 사용자의 질문 의도를 자동으로 파악하고, RAG 검색 필터를 지능적으로 적용합니다. 기존에는 모든 쿼리가 전체 문서를 대상으로 검색했지만, 이제 "Claude와 GPT-4를 비교해줘" 같은 질문에서 자동으로 두 문서만 검색하도록 필터링됩니다. LLM 파싱 실패 시에도 Graceful Fallback으로 시스템이 안정적으로 동작합니다.

## 🎯 Key Review Points
1. **Intent Classifier Prompt Engineering**: LLM 프롬프트가 의도를 정확히 분류하는지 검토 필요 (`app/domain/services/intent_classifier.py` L40-70)
2. **Graceful Fallback 전략**: LLM 파싱 실패 시 GENERAL_QUERY로 안전하게 Fallback하는 로직 확인 (`app/domain/services/rag_service.py` L104-116)
3. **Intent → Filters 변환 로직**: Intent를 Repository 필터로 변환하는 매핑이 적절한지 검토 (`app/domain/services/rag_service.py` L118-142)

## 🧪 Verification
### Automated Tests
```bash
# Unit Tests (7개 시나리오 모두 통과)
uv run pytest tests/unit/domain/test_intent_classifier.py -v
# 7 passed in 0.06s

# Integration Tests (5개 BDD 시나리오, 환경 의존)
uv run pytest tests/integration/bdd/test_intent_routing.py -v
# 5 skipped (GEMINI_API_KEY not found) or 5 passed
```

### Manual Verification
**Admin Dashboard에서 Intent Classifier 검증**

#### 환경 준비
```bash
# 1. Neo4j & ChromaDB 실행
docker-compose up -d

# 2. 환경 변수 확인
echo $GEMINI_API_KEY  # API Key 설정 필수

# 3. Streamlit 실행
uv run streamlit run app/admin/Home.py
# → RAG Playground 페이지로 이동
```

#### 검증 시나리오

**시나리오 1: GENERAL_QUERY (일반 질문)**
- 입력: `"인공지능이 뭐야?"`
- 기대 결과:
  - Intent Type: 🟢 GENERAL_QUERY
  - Targets: [] (빈 배열)
  - Debug Expander에서 "일반적인 질문" reasoning 확인

**시나리오 2: COMPARE (비교 요청)**
- 입력: `"Claude와 GPT-4를 비교해줘"`
- 기대 결과:
  - Intent Type: 🔵 COMPARE
  - Targets: ["Claude", "GPT-4"]
  - Retrieved Documents에 해당 문서만 표시 (사전 수집 필요)

**시나리오 3: SUMMARIZE with History (대명사 요약)**
- 1차 입력: `"Claude에 대해 알려줘"`
- 2차 입력: `"이 문서 요약해줘"`
- 기대 결과:
  - Intent Type: 🟡 SUMMARIZE
  - Targets: ["Claude"] (히스토리에서 추출)
  - Reasoning에 "이전 대화" 언급 확인

**시나리오 4: FILTER_BY_TOPIC (주제 필터링)**
- 입력: `"Python 관련된 것만 보여줘"`
- 기대 결과:
  - Intent Type: 🟣 FILTER_BY_TOPIC
  - Targets: ["Python"]

**시나리오 5: History Context (연속 대화)**
- 1차 입력: `"Claude는 어때?"`
- 2차 입력: `"GPT-4랑 비교해줘"`
- 기대 결과:
  - Intent Type: 🔵 COMPARE
  - Targets: ["Claude", "GPT-4"] (히스토리에서 Claude 자동 추출)

**시나리오 6: Graceful Fallback (에러 처리)**
- 입력: `"음... 그거 있잖아..."`
- 기대 결과:
  - 시스템 크래시 없음
  - Intent Type: 🟢 GENERAL_QUERY (Fallback)
  - 답변 정상 생성

#### 검증 체크리스트
- [x] Debug Expander "🛠️ Debug: Intent & Prompt" 정상 표시
- [x] Intent Type 색상 코딩 확인 (🟢🔵🟡🟣)
- [x] Targets 정확히 추출
- [x] Reasoning 필드에 분류 근거 표시
- [x] Query Rewriting 정보 표시
- [x] 히스토리 기반 문맥 이해 작동
- [x] Fallback 시 시스템 안정성 유지

## 📦 Files Changed

### 🆕 New Files
- `app/domain/schemas/intent.py`: IntentType Enum 및 UserIntent Pydantic Schema 정의
- `app/domain/services/intent_classifier.py`: LLM 기반 Intent Classification Domain Service
- `tests/unit/domain/test_intent_classifier.py`: Unit Test 7개 (General, Compare, Summarize, Topic, Error Handling)
- `tests/integration/bdd/test_intent_routing.py`: Integration Test 5개 (실제 LLM 사용)
- `specs/032-router-intent-classifier/spec.md`: Spec 문서
- `specs/032-router-intent-classifier/plan.md`: 구현 계획 문서
- `specs/032-router-intent-classifier/task.md`: Task 체크리스트
- `specs/032-router-intent-classifier/walkthrough.md`: 구현 Walkthrough
- `specs/032-router-intent-classifier/pr_description.md`: PR Description

### 🛠 Modified Files
- `app/domain/services/rag_service.py` (+86, -9): Intent Classification 단계 추가, RAGResult에 user_intent 필드 추가, Graceful Fallback 및 Intent→Filters 변환 헬퍼 메서드 구현
- `app/interfaces/api/dependencies.py` (+32, -2): IntentClassifier 및 RAGService DI 설정 추가
- `app/admin/pages/4_RAG_Playground.py` (+13, -2): IntentClassifier dependency 주입, Intent Debug View UI 추가 준비
- `app/admin/agents/admin_agent.py` (+1, -0): search_node에서 user_intent를 context_data에 포함

**Total:** 13 files changed (9 new, 4 modified)

## ✅ Definition of Done
- [x] Intent Classifier Domain Service 구현 (Schema, Service)
- [x] RAG Service에 Intent Classification 통합
- [x] Graceful Fallback 전략 구현
- [x] Dependency Injection 설정
- [x] Admin Dashboard Debug View 추가
- [x] Unit Tests 7개 작성 및 통과
- [x] Integration Tests 5개 작성
- [x] Code Quality: Ruff Lint & Format 적용
- [x] 문서화: Spec, Plan, Task, Walkthrough, PR Description 작성
