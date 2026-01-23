# Spec 032: Router & Intent Classifier (Decision Layer)

## 📋 배경 및 문제 정의 (Background & Problem)

### 현재 상황
**Spec 031**에서 Source-Filtered RAG를 구현하여 Repository 레벨에서 필터링 기능(`filters` 파라미터)을 제공했으나, 현재 시스템은 다음과 같은 한계가 있습니다:

1. **수동 필터 의존**: 사용자가 `filters={"id": ["A", "B"]}`를 명시적으로 전달해야만 특정 문서 검색 가능
2. **의도 파악 불가**: "A와 B를 비교해줘"라는 자연어 질문에서 시스템이 스스로 `targets: ["A", "B"]`를 추출하지 못함
3. **프롬프트 의존**: LLM에게 "관련 없는 문서는 무시해"라는 암묵적 지시만 하고, 물리적 검색 범위를 제한하지 않음 (Hallucination 유발)

### 문제점
- **Implicit State (암묵적 상태)**: 검색 범위가 프롬프트 텍스트에만 의존하여 LLM이 환각(Hallucination)할 수 있음
- **Decision-Execution 미분리**: "무엇을 검색할지"(결정)와 "실제 검색"(실행)이 혼재되어 제어 불가능

### 해결 방안
**Design Guide 005**에서 제시한 3-Layer 아키텍처를 구현:
- **Brain (LLM Router)**: 사용자 의도를 분석하고 검색 전략을 **결정**
- **Nervous System (LangGraph)**: 결정을 Retrieval Node로 **전달**
- **Memory/Body (RAG System)**: 결정을 **물리적으로 강제** 실행

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **Intent Classification**: 사용자 쿼리에서 의도(Intent) 파악
   - `general_query`: 일반 검색 (전체 지식 베이스 조회)
   - `compare`: 특정 문서들 비교 (예: "A와 B 비교")
   - `summarize`: 특정 문서 요약 (예: "이 문서 요약해줘")
   - `filter_by_topic`: 특정 주제/카테고리 필터링

2. **Target Extraction**: 의도에 따라 검색 대상(targets) 추출
   - Document ID, URL, Entity Name 등을 구조화된 형태로 반환
   - 예: `{"intent": "compare", "targets": ["doc_A", "doc_B"]}`

3. **Structured Output**: Pydantic 모델을 사용한 LLM 출력 검증
   - 잘못된 형식의 응답 거부 및 Fallback 처리

4. **RAG Service Integration**: 기존 `RAGService.retrieve_and_generate()`에 Router 통합
   - Router → Filters 변환 → Hybrid Search 흐름

### Non-Functional Requirements
1. **Latency**: Router 호출이 전체 RAG 파이프라인에 +200ms 이하 추가
2. **Reliability**: LLM 파싱 실패 시 Graceful Degradation (전체 검색으로 Fallback)
3. **Observability**: Admin Dashboard에서 Intent 결정 과정 디버그 가능
4. **Testability**: Mock LLM을 사용한 단위 테스트 가능

## ✅ Definition of Done
1. `IntentClassifier` Domain Service 구현 및 단위 테스트 통과
2. `RAGService`에 Router 통합 및 Integration Test 통과
3. Admin Dashboard에 Intent Debug View 추가
4. 전체 테스트 스위트 통과 (`pytest` + `ruff check`)
5. Documentation 업데이트 (`docs/architecture/rag_pipeline.md`)
