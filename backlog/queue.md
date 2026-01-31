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
  > 
  > **현재 문제점**:
  > - ❌ 특정 DB 상태를 가정하고 작성됨
  > - ❌ Docker 서비스 실행 여부 확인 안함
  > - ❌ 테스트 간 데이터 격리 미흡
  > - ❌ 실행 순서 의존성 존재

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

## 🕸️ Phase 4: Graph Construction (Topology)

> **목표**: 지식 그래프(Knowledge Graph)의 뼈대인 노드와 관계를 구축한다.

* [x] **Spec 010: Knowledge Graph Construction**
  * [x] Entity를 Neo4j 노드로 매핑
  * [x] Document-Entity MENTIONS 관계 생성
  * [x] Entity 조회 API 엔드포인트 추가

* [x] **Spec 016: Entity-Entity Relationship Extraction**
  * [x] LLM Prompt에 Entity 간 관계 추출 지시 추가
  * [x] 추출된 관계를 Neo4j에 저장 (FOUNDED, WORKS_FOR, USES 등)
  * [x] Relationship 기반 Graph 탐색 API 개발
  * [x] Entity Type 확장 (7개 → 9개: PRODUCT, DOCUMENT 추가)
  * **Note**: ChromaDB embedding 이슈 4개는 별도 Spec으로 처리 필요

* [x] **Spec 017: Embedding Strategy Refactoring**
  * [x] ChromaDB embedding을 Gemini Embedding API로 전환
  * [x] Heavy ML dependencies 제거 (onnxruntime, tokenizers)
  * [x] 4개 실패 integration test 수정
    - test_successful_entity_graph_auto_construction
    - test_entity_based_document_search
    - test_entity_deduplication
    - test_duplicate_url_sequential_ingestion
  * [x] Docker 컨테이너 경량화 (862MB)
  * [x] Entity Endpoint URL Encoding 버그 수정
  * [x] API Key Clean up (`GOOGLE_API_KEY` 제거)

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

* [x] **Spec 014: Code Quality Improvement**
  * [x] Bug Fix: semantic_data NameError 수정
  * [x] Test Standardization: TDD 테스트 GWT 형식 통일 (9개 파일)
  * [x] Module Docstring 한국어화 (12개 파일)
  * [x] 전체 테스트 통과 확인 (85 passed, 4 skipped)

* [x] **Spec 015: Documentation Update & Reorganization** 
  * [x] README 최신화 (Spec 010-015, Phase 4-5 반영)
  * [x] specs 디렉토리의 재사용 가능한 문서를 docs로 이동
  * [x] docs 디렉토리 구조 개선 (카테고리 분류)
  * [x] 전체 문서 일관성 검토 및 cross-reference 정리

* [x] **Spec 018: System Stability & Test Refactoring**
  * [x] **Refactor Exception Handling**: 명시적 예외 처리 및 커스텀 예외 계층 정의
  * [x] **Harden Repositories**: Null Safety 강화 및 Transaction 적용
  * [x] **Fix & Enable Tests**: Skipped Test(4개) 복구 및 `unit/test_scraper.py` 수정
  * [x] **Remove Anti-patterns**: `print()` -> `logging` 전환

---

## 🗺️ Roadmap (계획된 작업)

### Phase 3: Progressive Intelligence (계속)

---


### Phase 5: Knowledge Reasoning & Agentic Ecosystem (Current)

> **목표**: 구축된 그래프 위에서 추론(Reasoning)하고, 외부 도구와 연동하여 자동화된 지식 생산 생태계를 완성한다.

* [x] **Spec 019: Advanced Chunking Strategy**
  * [x] LangChain `RecursiveCharacterTextSplitter` 도입 (Context Overlap 적용)
  * [x] 문서(Document) -> 청크(Chunk) 1:N 구조 설계 및 저장
  * [x] Chunk 별 임베딩 및 Parent Document 참조 구현
  * **목표**: 긴 문서를 의미 단위로 쪼개어 검색 정확도(Semantic Search) 대폭 향상

* [x] **Spec 020: Transition to LangGraph**
  * [x] 복잡한 순환 참조 및 상태 관리를 위해 LangChain → LangGraph 마이그레이션 수행

* [x] **Spec 021: Logic Resolver (Conditional & Retry)**
  * [x] `validate_content` 결과에 따른 조건부 분기(Conditional Edges) 구현
  * [x] `IngestionState`에 `validation_feedback` 및 `previous_attempts` 추가 (Reflexion)
  * [x] LLM 재시도 루프(Retry Loop) 및 `retry_count` 제어 로직 추가
  * [x] 지식 간 모순(`Contradicts`) 및 보완 관계 자동 탐지 (Optional)
  * **Note**: Polymorphic Backtracking (Correction, Relaxation) 적용됨.

* [x] **Spec 022: Human-in-the-loop (Checkpointer)**
  * [x] LangGraph Checkpointer 도입 (Memory/DB) (ADR 020 Phase 3)
  * [x] 신뢰도 낮은 결과에 대한 `interrupt` 및 사용자 승인 대기
  * [x] 수정된 상태로 그래프 실행 재개 (`resume`)
  * **Note**: In-Memory Checkpointer (MemorySaver) 사용. Persistence는 Icebox에 추가됨.

* [x] **Spec 023: Reasoning Context & Failure Analysis**
  * **Design Guide**: [`docs/design_guides/reasoning_context.md`](docs/design_guides/reasoning_context.md)
  * **Documents**: [Spec](specs/023-reasoning-context/spec.md), [Plan](specs/023-reasoning-context/plan.md), [Task](specs/023-reasoning-context/task.md)
  * [x] **Backtracking Context**: `FailureHypothesis`, `DecisionTrace` 등 사고 기록 State 추가
  * [x] **Failure Analyzer Node**: LLM/Rule 기반 실패 원인 분석 (Reasoning Log)
  * [x] **Intelligent Prompting**: 단순히 결과를 알려주는 게 아니라 "왜 실패했는지" 원인을 포함하여 재시도 요청
  * [x] **Reasoning Visualization**: Trace Log에 사고 과정을 명확히 남김 (State Level)

* [x] **Spec 024: Advanced Admin Dashboard (Observability & HITL)**
  * [x] **Graph Explorer**: Neo4j 지식 그래프 시각화 (Interactive Network View)
  * [x] **HITL Control Center**: `interrupt` 상태 스레드 조회 및 Resume 연동
  * [x] **RAG Playground**: 
    - Retrieve-Generate 흐름 통합
    - General Knowledge Fallback (Clean Prompting)
    - Debug View (Prompt & Logic Inspection) (Feedback: [Design Guide 002](docs/design_guides/002-data-storage-strategy.md))
  * [x] **Reasoning Trace Viewer**: (Basic) HITL 화면에 Trace 연동

* [x] **Spec 025: Contextual RAG (Query Rewriting)**
  * [x] **Problem**: 현재 RAG는 단발성 검색(Single-turn)만 지원하여 "그 사람은?" 같은 대명사/문맥 질문에 실패함.
  * [x] **Goal**: 대화 이력(Chat History)을 기억하고, 이를 바탕으로 모호한 질문을 "완전한 검색 쿼리"로 변환(Rewriting)하는 모듈 추가.
  * [x] **Scope**:
    - `QueryRewriter` 컴포넌트 (LLM 기반)
    - Playground에 Multi-turn Session 적용
    - Chat History 관리
  * **Design Guide**: [`docs/design_guides/003-contextual-rag-cot.md`](docs/design_guides/003-contextual-rag-cot.md)

* **Phase 5: Retrieval Quality & Advanced RAG** (Deep Dive)
  * [x] **Spec 026: Hybrid RAG & Metadata Strategy**
    - **Strategic Flaws (In-sil-jik-go)**:
        1.  **Metadata Underutilization**: LLM에게 `Content`만 제공하여 URL 등 출처 정보를 환각(Hallucination)하는 문제 발생. `Chunk`의 풍부한 메타데이터(Title, Source, Author)를 버리고 있음.
        2.  **Fake Hybrid RAG**: 저장(`save`)은 Graph+Vector에 다 하지만, 정작 검색(`search`)은 **Vector DB(Chroma)만 사용**하고 있음. Graph DB(Neo4j)는 Write-Only 상태.
    - **Goal**:
        - `DocumentRepository.search`가 Neo4j와 Chroma를 모두 조회하도록 개선 (Hybrid Search).
        - `Standardized Context Format`: LLM에게 제공하는 청크 포맷을 `[Source ID] Title: ... Content: ...` 형태로 표준화하여 Citation 강제.
        - **Reranking**: 두 검색 결과를 통합(Merge)하고 점수화하는 전략 수립.
    - **Priority**: High (System Reliability Crisis)
    - **완료**: 2026-01-22 (Spec Implemented & Verified)
    - **Design Guide**: [`docs/design_guides/004-graph-rag-strategy.md`](docs/design_guides/004-graph-rag-strategy.md)

* [x] **Spec 027: Intelligent Web Scraping (Content Cleaning)**
  * [x] **Problem**: 현재 `BasicWebScraper`의 단순 변환(HTML->Markdown)으로 인해 광고, 댓글, 네비게이션 등 노이즈 데이터가 RAG에 유입됨(정보 오염).
  * [x] **Goal**: `readability` 알고리즘 및 노이즈 필터링을 적용하여 "순수 본문"만 정밀하게 추출.
  * [x] **Action**:
    - `trafilatura` 라이브러리 도입 (Readability + Fallback)
    - 광고/불필요 태그(`script`, `style`, `nav`, `footer`) 자동 제거
    - Metadata(Title, Author) 추출 강화
  * **Design Guide**: (TBD)


* [x] **Spec 028: Agentic MCP Server (Active Ingestion)**
  * [x] **Goal**: 외부 LLM(Claude, Cursor 등)이 대화 도중 주도적으로 정보를 수집하고 지식을 검색할 수 있도록 "도구(Tool)"를 제공하는 MCP(Model Context Protocol) 서버 구축.
  * [x] **Features**:
    - **Active Ingestion**: `ingest_url(url)` 도구를 통해 사용자가 던져준 링크를 즉시 학습.
    - **Knowledge Search**: `search_knowledge_base(query)` 도구로 RAG 검색 수행.
    - **Stdio/SSE Support**: 다양한 클라이언트 지원을 위한 표준 프로토콜 구현.

* [x] **Spec 029: Admin Agentic Workflow (LangGraph Integration)**
  * [x] **Goal**: Admin Dashboard(Streamlit)의 챗봇을 단순 Chain에서 "Agentic Workflow"로 업그레이드하여, 사용자의 의도(수집 vs 검색)를 파악하고 적절한 도구를 호출하게 함.
  * [x] **Features**:
    - **LangGraph Integration**: `4_RAG_Playground.py`에 LangGraph 기반 Agent 도입.
    - **Router Node**: 사용자 발화에서 URL 감지 시 수집 모드로, 질문 시 검색 모드로 분기.
    - **Tools Integration**: Spec 028에서 만든 `IngestionService`와 `RAGService`를 도구화.

---


* [x] **Spec 031: Source-Filtered RAG (Contextual Isolation)**
  * [x] **Problem**: RAG 검색 시 전체 지식 베이스를 조회하므로, 특정 문서를 요약해달라는 요청에도 타 관련 문서의 청크가 섞여 들어옴 (예: 위키피디아 링크를 요약 요청했는데 나무위키 내용이 나옴).
  * [x] **Goal**:
    - 검색(Retrieval) 시 `source_id` 또는 `url`로 범위를 제한하는 필터링 기능 추가.
    - Admin UI 및 API에서 "이 문서랑만 대화하기(Chat with Doc)" 모드 지원.
  * [x] **Action**:
    - `RAGService.retrieve` 메소드에 필터 파라미터 추가.
    - Vector DB 조회 시 Metadata Filter 적용.

* [x] **Spec 032: Router & Intent Classifier (Decision Layer)**
  * [x] **Goal**: LLM을 사용하여 사용자의 의도(Intent)를 분류하고, 데이터 검색이 필요한지 여부와 어떤 필터를 적용할지 "결정(Decision)"하는 라우터 노드 구현.
  * [x] **Output**: `{"intent": "compare", "targets": ["doc_A", "doc_B"]}` 형태의 구조화된 데이터.
  * **Reference**: [Design Guide 005: LLM RAG Strategy](docs/design_guides/005-llm-rag-strategy.md)
  * **Note**: Planning 중 (2026-01-23) - [Spec](specs/032-router-intent-classifier/spec.md), [Plan](specs/032-router-intent-classifier/plan.md)

* [x] **Spec 033: LangGraph State Management (Nervous System)**
  * [x] **Goal**: Router의 결정을 `GraphState`에 저장하고, 이를 `RetrievalNode`로 정확히 전달하여 실행을 강제하는 흐름 제어 구현.
  * [x] **Review Findings**: 시나리오 1~3 테스트를 통해 자동 필터링의 배타성, DB 메타데이터 불일치, Context 부재 시 LLM의 답변 성향 분석 완료. ([`rag_pipeline.md`](docs/architecture/rag_pipeline.md) TroubleShooting 섹션 참조)

* [x] **Spec 034: RAG Pipeline Recovery & Stability (Back To Baseline)**
  * [x] **Goal**: Spec 033 리뷰에서 발견된 검색 실패 시나리오를 해결하고 시스템 인프라(Checkpointer) 안정화.
  * [x] **Features**:
    - **Filter Fallback**: 필터 결과 0건 시 자동으로 Filter-less Global Search 수행.
    - **Empty Guard**: Context 부재 시 답변 거부 프롬프트 강화 (Hallucination 방지).
    - **Checkpointer Stability**: `checkpoints.sqlite` 파일 안정화 및 Playground 연동 수정.

* [x] **Spec 035: Transparent Hybrid Knowledge Strategy (RAG Resilience)**
  * **Documentation**: [`docs/architecture/rag_pipeline.md`](docs/architecture/rag_pipeline.md#rag-evolution-from-strict-to-hybrid)
  * [x] **Goal**: "Strict RAG"의 한계를 극복하기 위해 DB 정보와 LLM 지식을 지능적으로 융합하고, 출처(Citation)를 투명하게 제공하여 신뢰도와 사용성을 동시에 확보.
  * [x] **Features**:
    - **Hybrid Reasoning**: DB 검색 결과와 LLM의 내부 지식을 결합한 답변 생성 로직.
    - **Granular Citations**: 답변 내 인라인 인덱스(`[1]`) 및 하단 주석(Reference) UI 구현.
    - **Knowledge Source Distinction**: 답변 내에서 "DB 근거"와 "LLM 보충" 정보를 시각적으로 구분하여 사용자에게 알림.
  * **Status**: Planning (2026-01-24)

* [x] **Spec 037: RAG Quality Stabilization & Data Integrity Sync**
  * **Documentation**: [Spec](specs/037-rag-quality-stabilization/spec.md), [Plan](specs/037-rag-quality-stabilization/plan.md), [Task](specs/037-rag-quality-stabilization/task.md)
  * [x] **Problem**: 
    - **ChromaDB Drift**: Neo4j와 ChromaDB 간의 데이터 개수 불일치 (1401 vs 93).
    - **Metadata Loss**: 수집된 문서 중 제목(Title)이 누락된 경우가 많아 검색 품질 저하.
    - **Context Noise**: 위키피디아 등 복잡한 레이아웃의 마크다운 태그가 LLM의 추론 방해.
  * [x] **Goal**: 
    - **Data Synchronization**: Neo4j의 누락된 청크를 ChromaDB로 재인덱싱하는 동기화 도구 구현.
    - **Metadata Enrichment**: URL 및 본문 기반 제목 자동 추출 로직 강화.
    - **Context Cleaning**: LLM 전달 전 불필요한 마크다운 요소(네비게이션, 표 등) 정제.

* [x] **Spec 038: Structural Decoupling (Streamlit & Backend Separation)**
  * **Goal**: Streamlit Admin UI와 Backend 비즈니스 로직을 완전히 격리하여 독립적 배포 및 확장성을 확보.
  * **Features**:
    - **Admin API Layer**: 정합성 관리용 전용 API 엔드포인트(`admin/integrity/*`) 및 RAG 플레이그라운드 API 구축.
    - **Thin Client Refactoring**: Streamlit 내부의 직접 DB 접근 및 비즈니스 로직 임포트 제거.
    - **Infrastructure Isolation**: Docker Compose 설정을 변경하여 Streamlit의 DB 접근 권한 박살(격리).

* [x] **Spec 039: Advanced Scraper (Headless & Complex Layout Support)**
  * **Goal**: Playwright 또는 Selenium 기반의 Headless Browser 도입으로 렌더링된 최종 DOM을 수집하여 데이터 유실 없는 고품질 스크래핑 구현.
  * **Problem**: 현재 `trafilatura` 스크래퍼가 네이버 뉴스, 나무위키 등의 복잡한 레이아웃이나 일부 동적 렌더링을 필요로 하는 콘텐츠를 누락함.
  * **Action**:
    - `Firecrawl` 도입
    - Tiered Scraping Strategy 구현 (Trafilatura -> Headless Fallback)
    - Clean Markdown 변환 및 Noise Filtering 강화
  * **Status**: Planning (2026-01-26)
  * **Strategy**: [Design Guide 008](docs/design_guides/008-scrapper.md), [Design Guide 009](docs/design_guides/009-scapping-strategy.md)

* [x] **Spec 040: Real-World HITL Verification Script**
  * **Goal**: Mock이 아닌 실제 LLM과 상호작용하며 HITL 흐름을 검증하는 스크립트 작성 (`scripts/verify_hitl_real.py`).
  * **Scenario**: 실제 Gemini LLM 사용 -> 강제 오류 주입 -> Interrupt 확인 -> 수동 Resume -> 최종 결과 확인.
   품질 검증 단계에서 수행 권장.
  * **Status**: Completed (Merged)
  * **Documents**: [Spec](specs/040-hitl-verification-script/spec.md), [Plan](specs/040-hitl-verification-script/plan.md), [Task](specs/040-hitl-verification-script/task.md)

* [x] **Spec 041: Admin HITL UI & Robustness (Follow-up)**
  * **Goal**: HITL 모드에서 사용자가 직관적으로 "대기 상태"를 인지하고 제어(Resume/Approve)할 수 있는 UI를 구현하며, 구조적 안전장치를 강화함.
  * **Features**:
    - **Resume/Approve Button**: Streamlit Chat UI에 중단된 작업 재개 버튼 추가.
    - **Waiting State Indicator**: 답변 생성 후 "검토 대기 중" 상태 시각화.
    - **Architecture Documentation**: Checkpointer Collision Issue (`rag-{id}` namespace) 및 아키텍처 결정 기록.
  * **Context**: Spec 040에서 발견된 "답변 후 중단" UX 혼동 및 Backend Checkpointer 충돌 이슈에 대한 후속 조치.
  * **Status**: Completed (Merged)
  * **Documents**: [Spec](specs/041-hitl-ui-robustness/spec.md), [Plan](specs/041-hitl-ui-robustness/plan.md), [Task](specs/041-hitl-ui-robustness/task.md)

* [x] **Spec 042: DB Reset Architecture & Admin UI**
  * **Goal**: 개발 및 테스트 과정에서 오염된 데이터를 쉽게 초기화할 수 있도록 Admin UI에서 "DB Reset" 기능을 제공한다.
  * **Scope**: 
    - `POST /admin/integrity/reset` API 구현 (Neo4j, Chroma, SQLite, GraphState 초기화)
    - Admin UI에 "Danger Zone" 추가 및 초기화 버튼 연동.
    - **UI Persistence**: Streamlit 새로고침 시 대화 이력 및 상태 유지 구현 (History Reload).
  * **Design Guide**: (Spec 042 Artifacts)

* [x] **Spec 043: Robust Ingestion (Chroma Batching)**
  * **Problem**: '일론 머스크' 등 대형 문서(Chunk ~159개) 수집 시 ChromaDB 저장 단계에서 전체 실패(0건 저장) 발생.
  * **Cause**: 한 번에 너무 많은 청크를 임베딩/저장하려다 API Timeout 또는 Rate Limit 발생 추정.
  * **Goal**: `ChromaStorage.save_chunks`에 배치(Batch size=20) 로직을 도입하여 안정성 확보.

* [x] **Spec 044: Graph Retrieval Logic Fix (Entity-based Search)**
  * **Status**: Completed (Merged)
  * **Artifacts**: [Design Guide](docs/design_guides/010-graph-retrieval-logic.md), [Spec](specs/044-graph-retrieval-logic-fix/spec.md), [Plan](specs/044-graph-retrieval-logic-fix/plan.md), [Task](specs/044-graph-retrieval-logic-fix/task.md)
  * **Problem**: "일론과 트위터의 관계는?" 같은 질문 시 Entity 기반 검색이 되지 않아 답변 품질 저하.
  * **Solution**: `IntentClassifier`에서 Entity 추출 및 Neo4j Shortest Path (`find_shortest_path`) 구현으로 관계 정보 주입.
  * **PR**: `feat(spec-044): graph retrieval logic fix`

* [x] **Spec 045: Interactive Refinement (Canvas & Clarification)**
  * **Goal**: HITL UX를 "단순 승인"에서 "적극적 개입"으로 고도화.
  * **Features**:
    - **Clarification**: 모호한 질문 시 Agent가 역질문(Questions)을 하여 의도를 명확히 함.
    - **Canvas (Draft Editing)**: Agent가 작성한 초안을 사용자가 직접 수정(Edit) 후 최종 승인.
  * **Scenario**: 질문 ("이거 요약해") -> Agent ("어떤 문서요?") -> 답변 ("A문서") -> 초안 생성 -> 사용자 수정 -> 승인.
  * **Status**: Completed (2026-01-29)

* [x] **Spec 046: Advanced Scraper (Headless Browser)**
  * **Goal**: Playwright 도입으로 동적 페이지 및 복잡한 레이아웃 수집
  * **Action**: Tiered Scraping Strategy 구현 (Trafilatura -> Playwright Fallback).
  * **Status**: Completed (2026-01-29)

* [x] **Spec 047: YouTube Knowledge Scraper (Video-to-Knowledge)**
  * [x] **Goal**: YouTube 영상 유출 및 구조화된 지식 추출 (Docker 환경 동기화 포함).
  * [x] **Action**: Transcript API + Whisper Fallback + Docker `ffmpeg`/Playwright 설정.
  * **Status**: Completed (2026-01-29)

* [x] **Spec 049: Local File Ingestion (PDF, TXT, MD)**
  * [x] PDF/TXT/MD 로컬 파일 파싱 및 지식 인제스션
  * [x] Admin UI & Playground 파일 업로드 연동
  * **Priority**: High
  * **Status**: Completed (2026-01-30)

* [x] **Spec 050: Clean Architecture Refactoring (4-Layer Structure)**
  * **Goal**: 프로젝트 구조를 Clean Architecture 4-Layer로 전면 리팩토링
  * [x] **Phase A**: Dependency Rule 강제, Domain 재구성, Application Layer 통합
  * [x] **Phase B**: 네이밍 통일, Service Layer 정리, Protocol 적용
  * [x] **Phase C**: Architecture 문서 업데이트
  * **Results**:
    - 80 files changed (+2064, -333)
    - 22 commits (18 implementation + 4 documentation)
    - 126 passed tests (20 failed는 기존 이슈)
  * **Priority**: Critical (Architecture Debt)
  * **Status**: Completed (2026-01-31)
  * **PR**: [#55](https://github.com/Changsik00/rag-ingestion/pull/55)
  * **Follow-up**: DocumentMetadata VO, AdminAgent Renaming (Icebox 참조)

* [ ] **Spec 051: Architecture Refinement (Consistency & Cleanliness)**
  * **Goal**: Spec 050 P0 수정 이후 남은 구조적 개선 사항(P1~P3)을 반영하여 일관성 확보
  * **Guide**: [Design Guide 011: Architecture Refinement Strategy](docs/design_guides/011-architecture-refinement.md)
  * **Scope**:
    * **P1 (High)**: Service Suffix 제거(`Integrity`, `Feedback`), Chunk VO 이동, Chunker Protocol 도입
    * **P2 (Medium)**: AI Implementation 폴더 구조화, `file_processor` 위치 정리
    * **P3 (Low)**: Adapter 명확화(`Extractor`, `Orchestrator`), API v1 활용
  * **Status**: Ready to Start



---
---


### Phase 6: Future Vision

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

* **[Feature] RAG Advanced Settings & Debugging**
  * **Goal**: Playground의 "Advanced Settings"를 고도화하여 RAG 엔진의 세부 동작을 제어하고 가시성을 확보함.
  * **Action**:
    - **Hyperparameter Tuning**: 검색 결과 개수(Top-K), 검색 다양도(MMR Diversity), 모델 Temperature 조절 UI 추가.
    - **Advanced Debug View**: 유사도 점수(Score) 시각화, 지식 그래프 연결망 조회 등 상세 분석 도구 연동.
    - **Search Strategy Selector**: Vector Only, Hybrid, Graph Only 등 검색 엔진 모드 스위치 추가.

* **[Tech] Multi-Model Comparison**
  * 다양한 LLM(GPT, Claude 등)을 붙여 정보 추출 품질 및 비용 비교 분석

* **[Tech] E2E Testing with Playwright**
  * Playwright를 활용한 End-to-End 테스트 자동화
  * API 엔드포인트 통합 테스트
  * Admin Dashboard (Streamlit) UI 테스트
  * 전체 워크플로우 검증 (Ingest → Store → Retrieve)

* **[Tech] Semantic Chunking Upgrade**
  * 현재 Recursive 방식 대신 Google or OpenAI의 AI 기반 Semantic Chunking 도입 검토
  * 문맥 보존 성능과 비용/속도 트레이드오프 분석 필요
  * Spec 019 이후 검색 품질 개선이 추가로 필요할 때 진행
  * **Strategy**: [llm_strategy](docs/architecture/llm_strategy.md) (llm_strategy)
    
* **[Feature] HITL Persistence & Notification**
  * **Strategy**: [Design Guide 002](docs/design_guides/002-data-storage-strategy.md) (JSONL/SQLite vs Postgres)
  * **Persistence**: `PostgresSaver` 등을 도입하여 서버 재시작 시에도 결재 대기 상태 유지
  * **Notification**: `humne_review` 진입 시 Slack/Email 알림 발송
   Spec 022 완료 후 운영 단계에서 필요 시 진행

* **[Integration] n8n Workflow Automation**
  * **Goal**: 외부 소스(RSS/뉴스) 감지 시 자동 수집 트리거 및 알림 시스템.

* **[Tech] Metadata Robustness: Custom JSON Encoder**
  * **Problem**: 현재 `Neo4jDocumentRepository`와 `ChromaStorage`는 메타데이터를 `json.dumps`로 직렬화함. `datetime`이나 `bytes` 같은 객체가 포함되면 저장 실패 위험 있음.
  * **Solution**: `json.dumps` 호출 시 `default` 파라미터에 커스텀 인코더(datetime -> isoformat, bytes -> base64 등)를 주입하여 안정성 확보.
  * **Context**: Spec 049 로컬 파일 인제스션 작업 중 잠재적 위험으로 식별되어 등록.


* **[Refactor] DocumentMetadata Value Object (Spec 050 Follow-up)**
  * **Goal**: `Document.metadata: dict` 구조를 type-safe한 Value Object로 전환
  * **Trade-off**: 
    - 장점: 타입 안정성, IDE 자동완성, 명확한 스키마
    - 단점: 동적 메타데이터 추가 어려움, 리팩토링 비용
  * **Scope**: 
    - `DocumentMetadata` Value Object 정의
    - `Document` entity 수정
    - 모든 메타데이터 접근 코드 업데이트
  * **Context**: Spec 050 Phase A-2-3에서 스킵됨

* **[Refactor] AdminAgent Renaming (Spec 050 Follow-up)**
  * **Goal**: `AdminAgent` → `ConversationalRAGAgent`로 리네이밍하여 클라이언트 비의존적 naming 적용
  * **Breaking Change**: 모든 클라이언트 코드 수정 필요
  * **Scope**:
    - `app/application/services/admin_agent.py` → `app/application/clients/admin/rag_agent.py`
    - 클래스명 변경 및 import 경로 전면 업데이트
  * **Strategy**: 점진적 마이그레이션 (Deprecation Warning → 완전 교체)
  * **Context**: Spec 050 Phase C-1에서 Breaking Change가 너무 커서 스킵됨
