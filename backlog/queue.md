# 📋 Master Project Backlog (backlog/queue.md)

이 문서는 프로젝트의 전체 여정과 실행 우선순위를 관리하는 마스터 대시보드입니다. 모든 작업은 [`constitution.md`](../docs/constitution.md)의 **Backlog Law**를 준수하며, 사용자의 승인을 통해 **Spec**으로 승격되어 실행됩니다.

> **Note**: 완료된 작업(Phase 1~7)은 [🗄️ Archive](archive.md)로 이동되었습니다.


## 🚀 Phase 9: Advanced RAG Operations (Planning)

> **목표**: 운영 자동화 및 고급 RAG 기법 적용 (TBD)


## 🧊 Icebox (보류된 아이디어)

> **목표**: 언제 해도 상관없지만 보존할 가치가 있는 아이디어. 시간과 우선순위에 따라 Spec으로 승격될 수 있음.

* **[Testing] Integration Test Scenarios 확장** (Spec 009, 012의 잔여 작업)
  * 성공 시나리오: 다양한 콘텐츠 타입
  * 실패 시나리오: 타임아웃, 네트워크 오류, 빈 콘텐츠

* **[Feature] Admin Dashboard UX Improvement**
  * Job 상태 자동 갱신, 필터링/정렬

* **[Feature] Automated Scenario Test Suite (E2E Verification)**
  * API 기반 자동 시나리오 검증
  * LLM Judge를 통한 품질 자동 채점

* **[Feature] System Stability & Auto-Recovery**
  * DB 초기화 자동화
  * Ingestion Health Monitor

* **[Tech] Multi-Model Comparison**
  * 다양한 LLM(GPT, Claude 등) 성능/비용 비교

* **[Tech] E2E Testing with Playwright**
  * 전체 워크플로우(Ingest → Store → Retrieve) 검증

* **[Integration] n8n Workflow Automation**
  * 외부 소스 감지 및 자동 수집 트리거

* **[Tech] Semantic Chunking POC**
  * Google AI Semantic Chunker 비용 vs 품질 측정
  * Research Spec으로 진행 시 우선순위 상승 가능

* **[Tech] LLM-based Content Cleaner**
  * Ingestion 후처리에 LLM 도입
  * 노이즈 제거 자동화

* **[Frontend] Tech Stack Migration Study**
  * **Goal**: Streamlit → Next.js/React 타당성 검토
  * **Tasks**: POC 작성, 비교 보고서