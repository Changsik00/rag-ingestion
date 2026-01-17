# 📋 Master Project Backlog (backlog/queue.md)

이 문서는 프로젝트의 전체 여정과 실행 우선순위를 관리하는 마스터 대시보드입니다. 모든 작업은 `constitution.md`의 **Backlog Law**를 준수하며, 사용자의 승인을 통해 **Spec**으로 승격되어 실행됩니다.

## 🚨 Phase 1: The Functional Foundation (MVP)

> **목표**: 서버를 띄우고 실제 데이터를 수집하여 DB에 저장하는 "수직적 핵심 기능"을 완성한다.

### [EPIC-01] Core Pipeline & Persistence

* [x] **Spec 001: FastAPI & Web Collector Skeleton**
  * [x] `uv` 기반 아키텍처 및 FastAPI 서버 기동
  * [x] `POST /ingest/web` 엔드포인트 구현 (URL -> Markdown 반환)
  * [x] `pytest`를 이용한 서버 및 수집 로직 통합 테스트

* [x] **Spec 002: Atomic Storage & Swagger Admin**
  * [x] Neo4j(Graph) 및 ChromaDB(Vector) 기본 연동
  * [x] 수집 문서를 'Atomic Layer' 노드로 저장
  * [x] Swagger Docs를 통한 수집 결과물(Document) 조회 및 관리

---

## 🛠 Phase 2: Observability & Scalability (Admin)

> **목표**: 인제스션 과정을 모니터링하고, 대량 처리를 위한 비동기 환경을 구축한다.

### [EPIC-02] Backoffice & Async Ops

* [x] **Spec 003: Ingestion Admin Dashboard (Streamlit)**
  * [x] Ingestion Job Tracking (상태 관리)
  * [x] Streamlit Dashboard (모니터링 & 재시도)

* [x] **Spec 004: Async Processing & Task Status**
  * [x] `BackgroundTasks`를 이용한 비동기 인제스션 처리
  * [x] 작업별 상태(Pending/Running/Success/Fail) 추적 API

---

## 🧠 Phase 3: Progressive Intelligence (Ontology)

> **목표**: 단순 데이터를 "지식"으로 구조화하고 지능형 추출을 시작한다.

### [EPIC-03] Intent-Driven Structuring

* [x] **Spec 005: Basic Semantic Extraction**
  * [x] LangChain + Gemini 2.0 Flash 연동을 통한 기본 메타데이터 추출
  * [x] Title, Summary, Keywords, Entities 구조화 추출
  * [x] `SemanticExtractor` 도메인 서비스 구현
  * [x] 단위 및 통합 테스트 작성

* [x] **Spec 006: Clean Architecture Refactoring**
  * [x] Domain 레이어를 외부 프레임워크로부터 격리
  * [x] Python Protocol을 활용한 LLM 인터페이스 추상화
  * [x] Infrastructure에 LangChain Adapter 분리
  * [x] Ruff linter 도입 및 코드 품질 개선

* [x] **Spec 007: Ontology Design (Multi-layered)**
  * [x] 추출된 Entity를 목적별로 분류 (Person, Organization, Technology, Topic, etc)
  * [x] 관계 스키마 설계 (MENTIONS, RELATED_TO, CONTRADICTS, etc)

* [ ] **Spec 008: Knowledge Graph Construction**
  * [ ] Entity를 Neo4j 노드로 매핑
  * [ ] Entity 간 관계 생성 및 그래프 구축
  * [ ] Graph 탐색 API 개발
  * **Note**: 현재는 metadata의 entities를 JSON 문자열로 직렬화하여 저장 중. 향후 Entity를 별도 노드로 분리하여 관계 기반 쿼리 가능하게 개선 필요

---

## 🌐 Phase 4: Workflow & Ecosystem (Automation)

> **목표**: 외부 도구와 연동하여 자동화된 지식 생산 생태계를 완성한다.

### [EPIC-04] Advanced Automation & Connectivity

* [ ] **Tech Task: Transition to LangGraph**
  * [ ] 복잡한 순환 참조 및 상태 관리를 위해 LangChain → LangGraph 마이그레이션 수행


* [ ] **Spec 009: Logic Resolver (Deep Insight)**
  * [ ] 지식 간 모순(`Contradicts`) 및 보완 관계 자동 탐지

* [ ] **Spec 010: n8n Workflow Integration**
  * [ ] 외부 소스(RSS/뉴스) 감지 시 자동 수집 트리거 및 알림 시스템

* [ ] **Spec 011: MCP Server & Tree Visualization**
  * [ ] Claude/Obsidian 연동을 위한 MCP 서버 배포
  * [ ] 마인드맵용 계층 구조 JSON 생성 API 개발

---


## 📅 Future Roadmap

> **Note**: 미래의 Spec 번호는 잠정적이며, 진행 상황에 따라 변경될 수 있습니다. (예: Spec ???)

* **[EPIC-05] Local LLM Optimization**: Ollama 연동을 통한 보안/비용 절감 모드 지원.
* **[EPIC-06] Multi-Model Tiers**: 작업 난이도별 모델 자동 배분 로직.
* **[EPIC-07] User Feedback Loop**: 지식 추출 결과에 대한 사용자 피드백 반영 시스템.

---

## 🧊 Icebox (Ideas & Archive)

> **목표**: 현재 페이즈와 무관하게 보존할 아이디어 저장소.

* **[Tech] Multi-Model Comparison**: 다양한 LLM(GPT, Claude 등)을 붙여 정보 추출 품질 및 비용 비교 분석.
* **[Tech] E2E Testing with Playwright**: Playwright를 활용한 End-to-End 테스트 자동화
  * API 엔드포인트 통합 테스트
  * Admin Dashboard (Streamlit) UI 테스트
  * 전체 워크플로우 검증 (Ingest → Store → Retrieve)
