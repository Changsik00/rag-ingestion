# 📋 Master Project Backlog (backlog/queue.md)

이 문서는 프로젝트의 전체 여정과 실행 우선순위를 관리하는 마스터 대시보드입니다. 모든 작업은 [`constitution.md`](../docs/constitution.md)의 **Backlog Law**를 준수하며, 사용자의 승인을 통해 **Spec**으로 승격되어 실행됩니다.

> **Note**: 완료된 작업(Phase 1~4 및 Phase 5의 Spec 050까지)은 [🗄️ Archive](archive.md)로 이동되었습니다.

---

## 🧠 Phase 5: Knowledge Reasoning & Agentic Ecosystem (Completed)

> **목표**: 구축된 그래프 위에서 추론(Reasoning)하고, 외부 도구와 연동하여 자동화된 지식 생산 생태계를 완성한다.

* [x] **Spec 051: Architecture Refinement (Consistency & Cleanliness)** ✅
* [x] **Spec 052: Clean Architecture Layer Refinement** ✅
* [x] **Spec 053: API Standardization & Robustness** ✅
* [x] **Spec 054: Integration Test Infrastructure Improvement** ✅
  * **Goal**: 통합 테스트 신뢰성 확보를 위한 인프라 감지 및 시드 데이터 픽스처 구축
  * **Status**: ✅ Completed & Merged

---

## ⚡ Phase 6: Performance Optimization & Scalability (Current)

> **목표**: 시스템의 응답 속도, 처리량, 비용 효율성을 극대화하고 대규모 트래픽/데이터를 견딜 수 있는 구조로 최적화한다.

* [ ] **[Spec 055: RAG Precision & Advanced Settings](../specs/055-rag-precision-advanced-settings/spec.md)** (High) 🏃
  * **Goal**: 검색 품질 최적화 및 고급 튜닝 옵션 제공
  * **Scope**: Hyperparameter Tuning, Advanced Debug View, Search Strategy Selector

* [ ] **Spec 056: Local LLM Optimization** (Medium)
  * **Goal**: 로컬 모델(Ollama) 연동을 통한 비용 절감 및 속도 향상
  * **Scope**: Ollama Integration, Hybrid Model Routing

* [ ] **Spec 057: Semantic Chunking Upgrade** (Medium)
  * **Goal**: AI 기반 청킹 도입으로 인덱싱 품질 향상

* [ ] **Spec 058: API Input Validation & Error Handling** (Medium)
  * **Goal**: 클라이언트/프론트엔드 연동성을 위한 API 견고성 강화

---

## 🔮 Phase 7: Future Vision

> **목표**: 장기적인 비전 및 확장 계획

* [ ] **Multi-Model Tiers**: 작업 난이도별 모델 자동 배분 로직
* [ ] **User Feedback Loop**: 지식 추출 결과에 대한 사용자 피드백 반영 시스템
* [ ] **HITL Persistence & Notification**: PostgresSaver 도입 및 알림 시스템

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
