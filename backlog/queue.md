# 📋 Master Project Backlog (backlog/queue.md)

이 문서는 프로젝트의 전체 여정과 실행 우선순위를 관리하는 마스터 대시보드입니다. 모든 작업은 [`constitution.md`](../docs/constitution.md)의 **Backlog Law**를 준수하며, 사용자의 승인을 통해 **Spec**으로 승격되어 실행됩니다.

> **Note**: 완료된 작업(Phase 1~4 및 Phase 5의 Spec 050까지)은 [🗄️ Archive](archive.md)로 이동되었습니다.

---

## 🎨 Phase 7: User Experience & Observability 

> **목표**: Admin 대시보드를 단순 제어 패널에서 "지식 관리 및 분석 플랫폼"으로 격상시킨다.

* [x] **Spec 061: RAG Session Manual Cleanup & Admin Actions** (Completed)
  * **Goal**: Admin UI에서 테스트용 세션을 수동으로 생성하고, 필요 시 삭제할 수 있는 기능 구현
  * **Status**: ✅ Completed & Merged (PR #68)

* [x] **Spec 062: Refactor RAG API to Clean Architecture** (High) ✅
  * **Goal**: `rag.py`의 비대한 비즈니스 로직(SQL, Workflow Control, Mapper)을 Service/Domain 계층으로 분리하여 유지보수성 향상
  * **Tasks**:
    * `ConversationalRAGAgent` 내로 워크플로우 제어 로직 캡슐화
    * SQL 기반 세션 삭제 로직을 Repository/Service로 이동
    * DTO Mapper 클래스 분리

* [x] **Spec 063: Admin UI/UX Improvements** (High)
  * **Goal**: Graph Explorer/Playground UX 개선 및 Verification Lab 재설계.
  * **Current State**: Partial Implementation (Graph/Feedback Done, Lab Deferred).
  * **Tasks**:
    * **Graph Style**: Dark Mode 가시성 개선 (Done).
    * **Feedback**: UI 버튼 연동 (Done).
    * **Verification Lab**: 재설계 및 구현 (Deferred).

* [x] **Spec 064: RAG Observability Dashboard**
  * **Goal**: LangFuse/Arize Phoenix 연동, Token Usage/Latency 시각화.
  * **Current State**: Proposed.
  * **Tasks**:
    * **RAG Inspector**: 최근 요청의 단계별(Retrieval -> Rerank -> Generation) 로그 타임라인 뷰 구현
    * Server-side API Call Logging (Streamlit 한계 극복)

* [x] **Spec 065: Semantic De-Duplication (SDD)**
  * **Goal**: 중복 문서 수집 방지 및 의미 기반 중복 제거 (Content Hash & Semantic Check).
  * **Current State**: Proposed.
  * **Tasks**:
    * **Content Hash**: 문서 내용 기반 해시 생성 및 중복 체크.
    * **Semantic Check**: VectorDB 조회 통해 유사/중복 문서 식별.
    * **Force Refresh**: 강제 재수집 옵션 추가.

* [ ] **Spec 066: Enhanced Trace Viewer** (Medium)
  * **Goal**: Inspector에서 Rerank 단계의 상세 정보(점수, 필터링 사유, Drop된 청크)를 시각화하여 "왜 검색 안 됨?" 오해 해소.
  * **Context**: Current Inspector only shows vector search results, hiding the fact that chunks were filtered out by the Reranker.
  * **Tasks**:
    * Add `rerank_log` to RAGResult.
    * Visualize "Dropped Chunks" in Admin UI with their scores and reasoning.

* [ ] **Spec 067: Advanced Reranking Logic Research** (High)
  * **Problem**: 현재 Pointwise 방식은 정보가 파편화된 경우(context 부족) 개별 점수가 낮아 탈락함.
  * **Goal**: 여러 청크를 "함께" 고려하여 점수를 매기거나(Listwise), 상호 보완적인 정보를 살리는 로직 연구.
  * **Details (Listwise vs Pointwise)**:
    * **Pointwise (Current)**: Scores each chunk independently. Fast, but misses context split across chunks.
    * **Listwise (Proposed)**: Sends multiple chunks to LLM at once to evaluate the "set". better quality but higher latency/cost.
    * **Action Item**: Research Contextual Reranking or Sliding Window approaches to balance cost/performance.

---

## 🧊 Icebox (보류된 아이디어)

> **목표**: 언제 해도 상관없지만 보존할 가치가 있는 아이디어. 시간과 우선순위에 따라 Spec으로 승격될 수 있음.

* **[Testing] Integration Test Scenarios 확장** (Spec 009, 012의 잔여 작업)
  * 성공 시나리오: 다양한 콘텐츠 타입
  * 실패 시나리오: 타임아웃, 네트워크 오류, 빈 콘텐츠



* **[Feature] Admin Dashboard UX Improvement**

  * Job 상태 자동 갱신, 필터링/정렬

* **[Tech] Multi-Model Comparison**
  * 다양한 LLM(GPT, Claude 등) 성능/비용 비교 분석

* **[Tech] E2E Testing with Playwright**
  * 전체 워크플로우(Ingest → Store → Retrieve) 검증

* **[Integration] n8n Workflow Automation**
  * 외부 소스 감지 및 자동 수집 트리거

* **[Tech] Metadata Robustness: Custom JSON Encoder**

* **[Tech] Multi-Model Tiers: 작업 난이도별 모델 자동 배분 로직**

* **[Tech] User Feedback Loop: 지식 추출 결과에 대한 사용자 피드백 반영 시스템**

* **[Tech] HITL Persistence & Notification: PostgresSaver 도입 및 알림 시스템**

* **Frontend Tech Stack Migration Study** *
  * **Goal**: Streamlit의 한계를 극복하기 위한 Next.js/React 도입 타당성 검토 및 파일럿
  * **Tasks**:
    * Next.js + ShadcnUI로 핵심 페이지(Chat, Graph) POC 작성
    * Streamlit vs Next.js 기능/공수 비교 보고서