# 📋 Master Project Backlog (backlog/queue.md)

이 문서는 프로젝트의 전체 여정과 실행 우선순위를 관리하는 마스터 대시보드입니다. 모든 작업은 [`constitution.md`](../docs/constitution.md)의 **Backlog Law**를 준수하며, 사용자의 승인을 통해 **Spec**으로 승격되어 실행됩니다.

> **Note**: 완료된 작업(Phase 1~4 및 Phase 5의 Spec 050까지)은 [🗄️ Archive](archive.md)로 이동되었습니다.

---

## 🧠 Phase 5: Knowledge Reasoning & Agentic Ecosystem (Current)

> **목표**: 구축된 그래프 위에서 추론(Reasoning)하고, 외부 도구와 연동하여 자동화된 지식 생산 생태계를 완성한다.

* [x] **Spec 051: Architecture Refinement (Consistency & Cleanliness)** ✅
  * **Goal**: Spec 050 P0 수정 이후 남은 구조적 개선 사항(P1~P3)을 반영하여 일관성 확보
  * **Guide**: [Design Guide 012: Architecture Refinement Strategy](../docs/design_guides/012-architecture-refinement.md)
  * **Scope**:
    * **P1 (High)**: 
        - Service Suffix 제거(`Integrity`, `Feedback`)
        - Chunk VO 이동 및 Chunker Protocol 도입
        - **DocumentMetadata Value Object** (Type-safe Metadata)
    * **P2 (Medium)**: AI Implementation 폴더 구조화, `file_processor` 위치 정리
    * **P3 (Low)**: 
        - Adapter 명확화(`Extractor`, `Orchestrator`)
        - API v1 통합 및 `/admin/` 제거
        - **AdminAgent Renaming** (`ConversationalRAGAgent`로 변경)
  * **Status**: ✅ Completed & Merged
  * **PR**: [refactor: architecture refinement and api standardization (spec 051)](https://github.com/Changsik00/rag-ingestion/pull/XXX)

* [x] **Spec 052: Clean Architecture Layer Refinement** ✅
  * **Goal**: Spec 051 이후 남은 계층 경계 위반 및 네이밍 불일치 수정
  * **Scope**:
    * **P1 (High)**: 
        - Interface 계층 이동 (`llm`, `scraper` → `application/interfaces/`)
        - Service 계층 이동 (`feedback` → `application/services/`)
        - Value Object 정리 (`DocumentMetadata` → `value_objects/`)
    * **P2 (Medium)**: 
        - 파일명 표준화 (`admin_agent` → `agent`, `IngestionUseCase` → `Ingestion`)
        - Core 구조 단순화 (`core/utils/` 중첩 제거, `logger` 이름 통일)
    * **P3 (Low)**: 
        - State 파일 명확화 (`state.py` → `graph_state.py`)
        - 중복 파일 정리
  * **Status**: ✅ Completed (Verified in codebase)

* [x] **Spec 053: API Standardization & Robustness** ✅
  * **Goal**: API Response 표준화(DTO) 및 전역 예외 처리(Global Exception Handling) 적용
  * **Scope**:
    * **P1**: Common DTO (`BaseResponse`, `ErrorResponse`) 및 Domain DTO 정의
    * **P2**: 전역 예외 핸들러 (`error_handlers.py`) 구현 및 `try-except` 제거
    * **P3**: 모든 v1 Endpoint에 `response_model` 적용 및 Status Code 표준화 (`202 Accepted`)
  * **Status**: ✅ Completed (Verified in codebase)

* [ ] **Integration Test Infrastructure Improvement** 🆕
  > **문서**: [specs/integration-test-improvement.md](../specs/integration-test-improvement.md)  
  > **우선순위**: Medium  
  > **예상 소요**: 2-3일  
  > **목표**: Mock 데이터가 아닌 실제 데이터로 integration test를 수행할 수 있도록 테스트 인프라 개선
  > 
  > **현재 상태**: 16개 integration tests가 skip 처리됨 (실제 인프라 필요)
  > 
  > **주요 작업**:
  > * [ ] Docker 인프라 자동 확인 및 준비
  > * [ ] 테스트 데이터 시드 fixture 구현
  > * [ ] 시나리오 기반 테스트 재구성
  > * [ ] 테스트 격리 및 독립성 보장

---

## 🔮 Phase 6: Future Vision

> **목표**: 장기적인 비전 및 확장 계획

* [ ] **Local LLM Optimization**: Ollama 연동을 통한 보안/비용 절감 모드 지원
* [ ] **Multi-Model Tiers**: 작업 난이도별 모델 자동 배분 로직
* [ ] **User Feedback Loop**: 지식 추출 결과에 대한 사용자 피드백 반영 시스템

---

## 🧊 Icebox (보류된 아이디어)

> **목표**: 언제 해도 상관없지만 보존할 가치가 있는 아이디어. 시간과 우선순위에 따라 Spec으로 승격될 수 있음.

* **[Testing] Integration Test Scenarios 확장** (Spec 009, 012)
  * ✅ **완료 (Spec 012):** 잘못된 Job ID → 404, 중복 URL 처리
  * ⏳ **남은 작업:**
    - 성공 시나리오: 다양한 콘텐츠 타입
    - 실패 시나리오: 타임아웃, 네트워크 오류, 빈 콘텐츠
  * **상세 내용**: `specs/009-testing-strategy/remaining_scenarios.md` 참조

* **[Feature] API Input Validation & Error Handling Improvement**
  * Pydantic validator 강화
  * 명확한 에러 메시지 (한글/영문)
  * Swagger 문서 개선
  * **목적**: 프론트엔드/클라이언트 개발자에게 명확한 API 가드 제공

* **[Feature] Admin Dashboard UX Improvement**
  * Job 상태 자동 갱신 (Auto-refresh) 구현
  * Streamlit 실시간 업데이트 메커니즘 개선
  * Job 목록 필터링 및 정렬 기능 추가

* **[Feature] RAG Advanced Settings & Debugging**
  * **Goal**: Playground의 "Advanced Settings" 고도화.
  * **Action**:
    - **Hyperparameter Tuning**: Top-K, Diversity, TemperatureUI 추가.
    - **Advanced Debug View**: 상세 분석 도구 연동.
    - **Search Strategy Selector**: 검색 엔진 모드 스위치 추가.

* **[Tech] Multi-Model Comparison**
  * 다양한 LLM(GPT, Claude 등) 성능/비용 비교 분석

* **[Tech] E2E Testing with Playwright**
  * 전체 워크플로우(Ingest → Store → Retrieve) 검증

* **[Tech] Semantic Chunking Upgrade**
  * AI 기반 Semantic Chunking 도입 검토

* **[Feature] HITL Persistence & Notification**
  * `PostgresSaver` 도입 및 알림 시스템

* **[Integration] n8n Workflow Automation**
  * 외부 소스 감지 및 자동 수집 트리거

* **[Tech] Metadata Robustness: Custom JSON Encoder**
  * **Solution**: `json.dumps` 커스텀 인코더 주입으로 안정성 확보.


