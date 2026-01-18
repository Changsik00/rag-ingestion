# 📋 Master Project Backlog (backlog/queue.md)

이 문서는 프로젝트의 전체 여정과 실행 우선순위를 관리하는 마스터 대시보드입니다. 모든 작업은 `constitution.md`의 **Backlog Law**를 준수하며, 사용자의 승인을 통해 **Spec**으로 승격되어 실행됩니다.

> **Note**: Spec 번호는 실행 시점에 순차적으로 부여됩니다. Phase에 계획된 Spec이라도 급한 작업(리팩토링, 버그픽스, 개선)이 끼어들면 번호가 밀릴 수 있습니다.

---

## 🚨 Phase 1: The Functional Foundation (MVP)

> **목표**: 서버를 띄우고 실제 데이터를 수집하여 DB에 저장하는 "수직적 핵심 기능"을 완성한다.

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

* [x] **Spec 003: Ingestion Admin Dashboard (Streamlit)**
  * [x] Ingestion Job Tracking (상태 관리)
  * [x] Streamlit Dashboard (모니터링 & 재시도)

* [x] **Spec 004: Async Processing & Task Status**
  * [x] `BackgroundTasks`를 이용한 비동기 인제스션 처리
  * [x] 작업별 상태(Pending/Running/Success/Fail) 추적 API

---

## 🧠 Phase 3: Progressive Intelligence (Ontology)

> **목표**: 단순 데이터를 "지식"으로 구조화하고 지능형 추출을 시작한다.

* [x] **Spec 005: Basic Semantic Extraction**
  * [x] LangChain + Gemini 2.0 Flash 연동을 통한 기본 메타데이터 추출
  * [x] Title, Summary, Keywords, Entities 구조화 추출
  * [x] `SemanticExtractor` 도메인 서비스 구현
  * [x] 단위 및 통합 테스트 작성

* [x] **Spec 006: Clean Architecture Refactoring**
  > **목표**: 코드 품질 및 아키텍처 개선을 위한 리팩토링 작업. Phase 계획에는 없었지만 프로젝트 진행 중 필요성이 대두되어 수행한 작업들.
  * [x] Domain 레이어를 외부 프레임워크로부터 격리
  * [x] Python Protocol을 활용한 LLM 인터페이스 추상화
  * [x] Infrastructure에 LangChain Adapter 분리
  * [x] Ruff linter 도입 및 코드 품질 개선
  
* [x] **Spec 007: Ontology Design (Multi-layered)**
  * [x] 추출된 Entity를 목적별로 분류 (Person, Organization, Technology, Topic, etc)
  * [x] 관계 스키마 설계 (MENTIONS, RELATED_TO, CONTRADICTS, etc)
---

## 🐛 Unplanned (버그픽스)

> **목표**: 통합 환경에서 발견된 긴급한 버그 및 이슈 수정.

* [x] **Spec 008: Docker Integration Bugfix**
  * [x] Neo4jStorage 생성자 파라미터 불일치 수정
  * [x] Import 오류 수정
  * [x] Docker Compose 통합 환경 안정화
  * [x] Dockerfile 개선 (uv 기반 의존성 설치)

---

## 🧪 Unplanned (테스트 및 품질 개선)

> **목표**: 테스트 전략 및 품질 보증 체계 강화. 통합 환경에서만 발견되는 버그를 조기에 차단하기 위한 개선 작업.

* [x] **Spec 009: Testing Strategy Improvement**
  * [x] Contract Testing 도입 (인터페이스-구현체 계약 검증) - 32 passed, 2 skipped
  * [x] Integration Test 강화 (BDD, 예외 시나리오 집중) - 6 passed, 1 skipped
  * [x] 테스트 전략 문서화 (TDD vs BDD 가이드)
  * [x] BDD/TDD 테스트 구조 개선 및 Use Case Stories 작성
  * [x] 미구현 시나리오 문서화 (Icebox에 등록)

---

## Phase 3: Progressive Intelligence (계속)

* [x] **Spec 010: Knowledge Graph Construction**
  * [x] Entity를 Neo4j 노드로 매핑
  * [x] Document-Entity MENTIONS 관계 생성
  * [x] Entity 조회 API 엔드포인트 추가
  * **완료**: PR #12 머지 완료 (2026-01-18)

---

## 🛠 Unplanned (리팩토링 및 품질 개선)

> **목표**: 코드 품질, 일관성, 가독성 개선을 위한 리팩토링 작업.

* [x] **Spec 011: Infrastructure Layer Refactoring**
  * [x] Repository 파일명 표준화 (neo4j.py → neo4j_document_repository.py)
  * [x] 주석 한글 통일 (영어/한글 혼용 → 한글)
  * [x] Type hints 및 Clean Architecture 개선

---

## 🧪 Unplanned (테스트 회귀 수정)

> **목표**: Spec 006, 010, 011 이후 발생한 테스트 실패 수정.

* [x] **Spec 012: Integration Test High Priority Scenarios**
  * [x] 잘못된 Job ID → 404 에러 시나리오
  * [x] 중복 URL 처리 시나리오
  * [x] BDD 스타일 통합 테스트 추가

* [x] **Spec 013: Fix Failed Tests**
  * [x] DI 테스트 Import 경로 수정 (3개)
  * [x] Use Case 테스트 Mock 설정 업데이트 (3개)
  * [x] 전체 테스트 스위트 통과 확인 (85 passed, 4 skipped)
  * **완료**: 2026-01-18

---

## 🗺️ Roadmap (계획된 작업)

### Phase 3: Progressive Intelligence (계속)

* [ ] **Spec ???: Embedding Strategy Refactoring** (TBD)
  * [ ] ChromaDB default local embedding → API 기반 embedding 전환 (Gemini/OpenAI)
  * [ ] Heavy ML dependencies 제거 (onnxruntime, tokenizers)
  * [ ] Backend 컨테이너 경량화
  * [ ] Optional: Embedding worker 분리 아키텍처 고려
  * **현재 상태**: ChromaDB가 all-MiniLM-L6-v2 로컬 모델 사용 중 (간접 의존성으로 onnxruntime, tokenizers 필요)

---

### Phase 4: Workflow & Ecosystem (Automation)

> **목표**: 외부 도구와 연동하여 자동화된 지식 생산 생태계를 완성한다.

* [ ] **Spec ???: Transition to LangGraph** (TBD)
  * [ ] 복잡한 순환 참조 및 상태 관리를 위해 LangChain → LangGraph 마이그레이션 수행

* [ ] **Spec ???: Logic Resolver (Deep Insight)** (TBD)
  * [ ] 지식 간 모순(`Contradicts`) 및 보완 관계 자동 탐지

* [ ] **Spec ???: n8n Workflow Integration** (TBD)
  * [ ] 외부 소스(RSS/뉴스) 감지 시 자동 수집 트리거 및 알림 시스템

* [ ] **Spec ???: MCP Server & Tree Visualization** (TBD)
  * [ ] Claude/Obsidian 연동을 위한 MCP 서버 배포
  * [ ] 마인드맵용 계층 구조 JSON 생성 API 개발

---

### Phase 5+: Future Vision

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
    - Edge Cases: 매우 긴 URL, 매우 큰 HTML (10MB+), Redirect 처리
  * **상세 내용**: `specs/009-testing-strategy/remaining_scenarios.md` 참조
  * **우선순위**: Medium (High Priority 완료됨)


* **[Feature] API Input Validation & Error Handling Improvement**
  * Pydantic validator 강화
  * 명확한 에러 메시지 (한글/영문)
  * Swagger 문서 개선 (required, format, example)
  * HTTP 422 vs 400 명확한 구분
  * FastAPI exception handler 개선
  * **목적**: 프론트엔드/클라이언트 개발자에게 명확한 API 가드 제공

* **[Feature] Admin Dashboard UX Improvement**
  * Job 상태 자동 갱신 (Auto-refresh) 구현
  * Streamlit 실시간 업데이트 메커니즘 개선
  * Job 목록 필터링 및 정렬 기능 추가

* **[Tech] Multi-Model Comparison**
  * 다양한 LLM(GPT, Claude 등)을 붙여 정보 추출 품질 및 비용 비교 분석

* **[Tech] E2E Testing with Playwright**
  * Playwright를 활용한 End-to-End 테스트 자동화
  * API 엔드포인트 통합 테스트
  * Admin Dashboard (Streamlit) UI 테스트
  * 전체 워크플로우 검증 (Ingest → Store → Retrieve)
