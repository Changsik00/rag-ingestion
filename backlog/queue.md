# 📋 Master Project Backlog (backlog/queue.md)

이 문서는 프로젝트의 전체 여정과 실행 우선순위를 관리하는 마스터 대시보드입니다. 모든 작업은 [`constitution.md`](../docs/constitution.md)의 **Backlog Law**를 준수하며, 사용자의 승인을 통해 **Spec**으로 승격되어 실행됩니다.

> **Note**: 완료된 작업(Phase 1~7)은 [🗄️ Archive](archive.md)로 이동되었습니다.


## 🚀 Phase 9: Advanced RAG Operations (Planning)

> **목표**: 운영 자동화 및 고급 RAG 기법 적용. "Autonomous Knowledge Operations" 달성.


* [ ] **Spec 078: [Agentic] Autonomous Discovery (Research Crawler)**
  * **Goal**: 주제만 주어짐 -> 자율 탐색 -> 수집 -> 구조화
  * **Key Features**: Google Search Tool, HTML Parsing, Recursive Link Following
  * **Vision**: "사용자가 URL을 주지 않아도, 주제만 던지면 스스로 학습하는 에이전트"

* [ ] **Spec 079: [Synthesis] Knowledge Synthesis (Report Generator)**
  * **Goal**: 지식 그래프 서브그래프 추출 -> LLM 기반 리포트/챕터 작성
  * **Key Features**: Subgraph Extraction, Contextual Summarization, Markdown Report Generation
  * **Vision**: "단편적 질문-답변을 넘어, 완결된 지식 콘텐츠(Report)를 생산하는 공장"

* [ ] **Spec 080: [Ops] Operational Excellence (Continuous Evaluation)**
  * **Goal**: 답변 품질 자동 평가 및 RAG 파이프라인 모니터링
  * **Key Features**: LLM Judge, Feedback Loop (Thumbs up/down), Performance Metrics
  * **Vision**: "품질을 스스로 측정하고 개선하는 자가 발전 시스템"

* [ ] **Spec 081: [Integration] n8n Workflow Automation** (Promoted)
  * **Goal**: 외부 소스 감지 및 자동 수집 트리거
  * **Fit**: "Autonomous Discovery"의 수동적 탐색(Trigger) 보완

* [ ] **Spec 082: [Ops] System Stability & Auto-Recovery** (Promoted)
  * **Goal**: Ingestion Health Monitor & DB Auto-Reset
  * **Fit**: "Operational Excellence"의 필수 요소

* [ ] **Spec 083: [Quality] Automated Scenario Test Suite** (Promoted)
  * **Goal**: API 기반 시나리오 검증 & LLM Judge 채점
  * **Fit**: 품질 보증의 자동화


## 🧊 Icebox (보류된 아이디어)

> **목표**: 언제 해도 상관없지만 보존할 가치가 있는 아이디어. 시간과 우선순위에 따라 Spec으로 승격될 수 있음.

* **[Feature] Admin Dashboard UX Improvement**
  * Job 상태 자동 갱신, 필터링/정렬

* **[Tech] Multi-Model Comparison**
  * 다양한 LLM(GPT, Claude 등) 성능/비용 비교

* **[Tech] E2E Testing with Playwright**
  * 전체 워크플로우(Ingest → Store → Retrieve) 검증

* **[Tech] Semantic Chunking POC**
  * Google AI Semantic Chunker 비용 vs 품질 측정
  * Research Spec으로 진행 시 우선순위 상승 가능

* **[Tech] LLM-based Content Cleaner**
  * Ingestion 후처리에 LLM 도입
  * 노이즈 제거 자동화

* **[Frontend] Tech Stack Migration Study**
  * **Goal**: Streamlit → Next.js/React 타당성 검토
  * **Tasks**: POC 작성, 비교 보고서