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

* [ ] **Spec 064: RAG Observability Dashboard** (Medium)
  * **Goal**: 블랙박스 같은 RAG 내부 동작을 투명하게 시각화 (Trace Viewer)
  * **Tasks**:
    * **RAG Inspector**: 최근 요청의 단계별(Retrieval -> Rerank -> Generation) 로그 타임라인 뷰 구현
    * Server-side API Call Logging (Streamlit 한계 극복)

* [ ] **Spec 065: Frontend Tech Stack Migration Study** (Low)
  * **Goal**: Streamlit의 한계를 극복하기 위한 Next.js/React 도입 타당성 검토 및 파일럿
  * **Tasks**:
    * Next.js + ShadcnUI로 핵심 페이지(Chat, Graph) POC 작성
    * 개발 생산성 vs 사용자 경험 Trade-off 분석 보고서 작성

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