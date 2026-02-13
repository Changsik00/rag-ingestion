# 🗄️ Project Archive (backlog/archive.md)

이 문서는 완료된 Spec과 Phase를 보관하는 아카이브입니다.

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

* [x] **Spec 017: Embedding Strategy Refactoring**
  * [x] ChromaDB embedding을 Gemini Embedding API로 전환
  * [x] Heavy ML dependencies 제거 (onnxruntime, tokenizers)
  * [x] 4개 실패 integration test 수정
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

## 🧠 Phase 5: Knowledge Reasoning & Agentic Ecosystem (Partially Completed)

> **목표**: 구축된 그래프 위에서 추론(Reasoning)하고, 외부 도구와 연동하여 자동화된 지식 생산 생태계를 완성한다.

* [x] **Spec 019: Advanced Chunking Strategy**
  * [x] LangChain `RecursiveCharacterTextSplitter` 도입 (Context Overlap 적용)
  * [x] 문서(Document) -> 청크(Chunk) 1:N 구조 설계 및 저장
  * [x] Chunk 별 임베딩 및 Parent Document 참조 구현

* [x] **Spec 020: Transition to LangGraph**
  * [x] 복잡한 순환 참조 및 상태 관리를 위해 LangChain → LangGraph 마이그레이션 수행

* [x] **Spec 021: Logic Resolver (Conditional & Retry)**
  * [x] `validate_content` 결과에 따른 조건부 분기(Conditional Edges) 구현
  * [x] `IngestionState`에 `validation_feedback` 및 `previous_attempts` 추가 (Reflexion)
  * [x] LLM 재시도 루프(Retry Loop) 및 `retry_count` 제어 로직 추가
  * [x] 지식 간 모순(`Contradicts`) 및 보완 관계 자동 탐지 (Optional)

* [x] **Spec 022: Human-in-the-loop (Checkpointer)**
  * [x] LangGraph Checkpointer 도입 (Memory/DB) (ADR 020 Phase 3)
  * [x] 신뢰도 낮은 결과에 대한 `interrupt` 및 사용자 승인 대기
  * [x] 수정된 상태로 그래프 실행 재개 (`resume`)

* [x] **Spec 023: Reasoning Context & Failure Analysis**
  * [x] **Backtracking Context**: `FailureHypothesis`, `DecisionTrace` 등 사고 기록 State 추가
  * [x] **Failure Analyzer Node**: LLM/Rule 기반 실패 원인 분석 (Reasoning Log)
  * [x] **Intelligent Prompting**: 단순히 결과를 알려주는 게 아니라 "왜 실패했는지" 원인을 포함하여 재시도 요청
  * [x] **Reasoning Visualization**: Trace Log에 사고 과정을 명확히 남김 (State Level)

* [x] **Spec 024: Advanced Admin Dashboard (Observability & HITL)**
  * [x] **Graph Explorer**: Neo4j 지식 그래프 시각화 (Interactive Network View)
  * [x] **HITL Control Center**: `interrupt` 상태 스레드 조회 및 Resume 연동
  * [x] **RAG Playground**: Retrieve-Generate 흐름 통합, General Knowledge Fallback, Debug View, Reasoning Trace Viewer

* [x] **Spec 025: Contextual RAG (Query Rewriting)**
  * [x] **Goal**: 대화 이력(Chat History)을 기억하고, 이를 바탕으로 모호한 질문을 "완전한 검색 쿼리"로 변환(Rewriting)하는 모듈 추가.
  * [x] **Scope**: `QueryRewriter` 컴포넌트, Multi-turn Session, Chat History 관리

* [x] **Spec 026: Hybrid RAG & Metadata Strategy**
  * [x] **Goal**: Graph+Vector 하이브리드 검색 및 표준화된 Citation 전략 수립.
  * [x] **Features**: Hybrid Reasoning, Granular Citations, Knowledge Source Distinction

* [x] **Spec 027: Intelligent Web Scraping (Content Cleaning)**
  * [x] **Goal**: `readability` 알고리즘 및 노이즈 필터링을 적용하여 "순수 본문"만 정밀하게 추출.
  * [x] **Action**: `trafilatura` 도입, 광고 제거, Metadata 추출 강화

* [x] **Spec 028: Agentic MCP Server (Active Ingestion)**
  * [x] **Goal**: 외부 LLM(Claude, Cursor 등) 연동용 MCP 서버 구축.
  * [x] **Features**: Active Ingestion, Knowledge Search, Stdio/SSE Support

* [x] **Spec 029: Admin Agentic Workflow (LangGraph Integration)**
  * [x] **Goal**: Admin Dashboard 챗봇을 Agentic Workflow로 업그레이드.
  * [x] **Features**: LangGraph Integration, Router Node, Tools Integration

* [x] **Spec 031: Source-Filtered RAG (Contextual Isolation)**
  * [x] **Goal**: 검색(Retrieval) 시 `source_id` 또는 `url`로 범위를 제한하는 필터링 기능.
  * [x] **Action**: `retrieve` 메소드 필터 파라미터 추가, Vector DB Metadata Filter

* [x] **Spec 032: Router & Intent Classifier (Decision Layer)**
  * [x] **Goal**: 사용자 의도 분류 및 검색 필요 여부 라우팅.

* [x] **Spec 033: LangGraph State Management (Nervous System)**
  * [x] **Goal**: Router 결정을 통한 강제 흐름 제어 및 검색 실패 시나리오 분석.

* [x] **Spec 034: RAG Pipeline Recovery & Stability (Back To Baseline)**
  * [x] **Goal**: 검색 실패 시나리오 해결 및 Checkpointer 안정화.
  * [x] **Features**: Filter Fallback, Empty Guard, Checkpointer Stability

* [x] **Spec 035: Transparent Hybrid Knowledge Strategy (RAG Resilience)**
  * [x] **Goal**: DB 정보와 LLM 지식의 투명한 융합.
  * [x] **Features**: Hybrid Reasoning, Granular Citations

* [x] **Spec 037: RAG Quality Stabilization & Data Integrity Sync**
  * [x] **Goal**: Neo4j-Chroma 데이터 동기화 및 메타데이터 강화.
  * [x] **Features**: Data Synchronization, Metadata Enrichment, Context Cleaning

* [x] **Spec 038: Structural Decoupling (Streamlit & Backend Separation)**
  * [x] **Goal**: Streamlit UI와 Backend 로직 격리.
  * [x] **Features**: Admin API Layer, Thin Client Refactoring, Infrastructure Isolation

* [x] **Spec 039: Advanced Scraper (Headless & Complex Layout Support)**
  * [x] **Goal**: Playwright 도입 및 Headless Browser Fallback.
  * [x] **Status**: Completed

* [x] **Spec 040: Real-World HITL Verification Script**
  * [x] **Goal**: 실제 LLM과 상호작용하는 HITL 검증 스크립트 작성.

* [x] **Spec 041: Admin HITL UI & Robustness (Follow-up)**
  * [x] **Goal**: HITL 대기 상태 시각화 및 UX 개선.

* [x] **Spec 042: DB Reset Architecture & Admin UI**
  * [x] **Goal**: Admin UI에서 DB 및 상태 전체 초기화 기능 제공.

* [x] **Spec 043: Robust Ingestion (Chroma Batching)**
  * [x] **Goal**: ChromaDB 대량 저장 시 배치 처리 도입.

* [x] **Spec 044: Graph Retrieval Logic Fix (Entity-based Search)**
  * [x] **Goal**: Entity 기반 검색 로직 개선 (Shortest Path).

* [x] **Spec 045: Interactive Refinement (Canvas & Clarification)**
  * [x] **Goal**: HITL UX 고도화 (역질문 및 초안 수정).

* [x] **Spec 046: Advanced Scraper (Headless Browser)**
  * [x] **Goal**: Tiered Scraping Strategy 구현.

* [x] **Spec 047: YouTube Knowledge Scraper (Video-to-Knowledge)**
  * [x] **Goal**: YouTube Transcript 추출 및 구조화.

* [x] **Spec 049: Local File Ingestion (PDF, TXT, MD)**
  * [x] **Goal**: 로컬 파일 파싱 및 인제스션.

* [x] **Spec 054: Integration Test Infrastructure Improvement** ✅
  * **Goal**: 테스트 신뢰도 향상을 위한 인프라 체크 및 데이터 격리 구조 도입
  * **Summary**: 인프라 상태 자동 감지 fixture 도입 및 테스트 스위트 재위계화 수행.

* [x] **Spec 050: Clean Architecture Refactoring (4-Layer Structure)**
  * [x] **Goal**: Clean Architecture 4-Layer 리팩토링 및 Dependency Rule 적용.

* [x] **Spec 055: RAG Precision & Advanced Settings** ✅
  * **Goal**: 검색 품질 최적화 및 고급 튜닝 옵션 제공 (Multimodal filter, Graph optimization, Raw API Output)

* [x] **Spec 056: Semantic Chunking Upgrade** ✅
  * **Goal**: Embedding Similarity 기반 의미 단위 청킹(Semantic Chunking) 구현 및 검색 밀도 향상

---

## 🧠 Phase 6: Performance Optimization & Scalability

* [x] **Spec 057: Unit Test Restructuring & Stability Upgrade**
  * **Goal**: Clean Architecture 레이어에 맞춘 테스트 구조 재정비 및 실패 테스트(7건) 정상화.
  * **Status**: ✅ Completed

* [x] **Spec 058: API Input Validation & Error Handling**
  * **Goal**: 클라이언트/프론트엔드 연동성을 위한 API 견고성 강화.
  * **Status**: ✅ Completed

* [x] **Spec 059: Docker Build Optimization**
  * **Goal**: Docker 빌드 속도 개선을 위한 Base Image 도입 및 의존성 캐싱 최적화.
  * **Status**: ✅ Completed

* [x] **Spec 060: Migrate from SQLite to Postgres Checkpointer**
  * **Goal**: 분산 환경 지원 및 동시성 처리를 위해 LangGraph Checkpointer를 SQLite에서 PostgreSQL로 마이그레이션.
  * **Status**: ✅ Completed

* [x] **Spec 061: RAG Session Cleanup & Expiration**
  * **Goal**: 오래된 RAG 세션을 주기적으로 정리하는 작업.
  * **Status**: ✅ Completed

* [x] **Spec 062: Refactor RAG API**
  * **Goal**: Clean Architecture 적용 및 API 리팩토링.
  * **Status**: ✅ Completed

---

## 🎨 Phase 7: User Experience & Observability

> **목표**: Admin 대시보드를 단순 제어 패널에서 "지식 관리 및 분석 플랫폼"으로 격상시킨다.  
> **Status**: ✅ **Completed** (2026-02-08)

* [x] **Spec 061: RAG Session Manual Cleanup & Admin Actions**
  * **Goal**: Admin UI에서 테스트용 세션을 수동으로 생성하고, 필요 시 삭제할 수 있는 기능 구현
  * **Status**: ✅ Completed & Merged (PR #68)

* [x] **Spec 062: Refactor RAG API to Clean Architecture** (High)
  * **Goal**: `rag.py`의 비대한 비즈니스 로직(SQL, Workflow Control, Mapper)을 Service/Domain 계층으로 분리하여 유지보수성 향상
  * **Tasks**:
    * `ConversationalRAGAgent` 내로 워크플로우 제어 로직 캡슐화
    * SQL 기반 세션 삭제 로직을 Repository/Service로 이동
    * DTO Mapper 클래스 분리

* [x] **Spec 063: Admin UI/UX Improvements** (High)
  * **Goal**: Graph Explorer/Playground UX 개선 및 Verification Lab 재설계
  * **Tasks**:
    * **Graph Style**: Dark Mode 가시성 개선 (Done)
    * **Feedback**: UI 버튼 연동 (Done)
    * **Verification Lab**: 재설계 및 구현 (Deferred)

* [x] **Spec 064: RAG Observability Dashboard**
  * **Goal**: LangFuse/Arize Phoenix 연동, Token Usage/Latency 시각화
  * **Tasks**:
    * **RAG Inspector**: 최근 요청의 단계별(Retrieval → Rerank → Generation) 로그 타임라인 뷰 구현
    * Server-side API Call Logging (Streamlit 한계 극복)

* [x] **Spec 065: Semantic De-Duplication (SDD)**
  * **Goal**: 중복 문서 수집 방지 및 의미 기반 중복 제거 (Content Hash & Semantic Check)
  * **Tasks**:
    * **Content Hash**: 문서 내용 기반 해시 생성 및 중복 체크
    * **Semantic Check**: VectorDB 조회 통해 유사/중복 문서 식별
    * **Force Refresh**: 강제 재수집 옵션 추가

* [x] **Spec 066: Enhanced Trace Viewer**
  * **Goal**: Inspector에서 Rerank 단계의 상세 정보(점수, 필터링 사유, Drop된 청크)를 시각화하여 "왜 검색 안 됨?" 오해 해소
  * **Tasks**:
    * Add `rerank_log` to RAGResult
    * Visualize "Dropped Chunks" in Admin UI with their scores and reasoning

* [x] **Spec 067: Advanced Reranking Logic Research**
  * **Goal**: 여러 청크를 "함께" 고려하여 점수를 매기거나(Listwise), 상호 보완적인 정보를 살리는 로직 연구
  * **Tasks**:
    * Listwise Reranking 전략 구현
    * Contextual (Sliding Window) 확장 기능 도입
    * Pointwise vs Listwise 전략 분기 구현
## 🏗️ Phase 8: Architecture & Quality Foundation

> **목표**: RAG 시스템의 근본적인 아키텍처 문제를 해결하고 품질 검증 인프라를 구축한다.
> **기반**: [**Spec 068: RAG System Architecture Review**](../specs/068-rag-architecture-review/README.md) 분석 결과

* [x] **Spec 068: RAG System Architecture Review**
  * [x] 시스템 전반의 아키텍처 진단 및 개선안 도출
  * [x] Clean Architecture 위반 사례 식별 (Brain Layer 등)
  * [x] 품질 검증 프로세스 부재 확인 및 개선 계획 수립

* [x] **Spec 069: Reranker Prompt Optimization**
  * [x] Rerank 정확도 향상을 위한 프롬프트 엔지니어링 수행
  * [x] 문서와 쿼리 간의 연관성 분석 로직 개선
  * [x] Golden Dataset 기반 성능 측정 (Recall +10%)

* [x] **Spec 070: Prompt Quality Testing Framework**
  * [x] 프롬프트 변경 시 자동화된 회귀 테스트 환경 구축
  * [x] 20개 이상의 필수 테스트 케이스 정의 (헌법 반영)
  * [x] LLM Judge 기반의 평가 파이프라인 도입

* [x] **Spec 071: ChromaDB Upsert Logic Improvement**
  * [x] 벡터 DB 데이터 중복 저장 문제 해결 (Upsert 로직 수정)
  * [x] Document ID 체계 정비
  * [x] 데이터 무결성 검증 스크립트 작성

* [x] **Spec 072: Robust Deduplication Framework**
  * [x] 수집 단계에서의 중복 콘텐츠 필터링 강화
  * [x] URL 정규화 및 Content Hash 기반 중복 제거
  * [x] Skip Rate 모니터링 추가

* [x] **Spec 073: Fuzzy Filter Matching Strategy**
  * [x] 사용자 쿼리의 오타/유의어를 처리하는 필터링 로직 구현
  * [x] Metadata 필터링 정확도 95% 달성
  * [x] 검색 실패 시 완화된 조건으로 재검색하는 Fallback 구현

* [x] **Spec 074: LLM Interface Clean Architecture**
  * [x] LLM 의존성을 도메인 영역에서 격리
  * [x] Port-Adapter 패턴을 적용한 LLM 인터페이스 추상화
  * [x] 다양한 모델(Gemini, Claude 등) 교체 용이성 확보

* [x] **Spec 075: Refined 3-Layer Brain Architecture**
  * [x] Brain Layer의 책임과 역할을 명확히 재정의
  * [x] 순환 참조 문제 해결을 위한 계층 구조 단순화
  * [x] Router, Reranker, Generator 간의 의존성 정리

* [x] **Spec 076: Ingestion Transaction Integrity**
  * [x] 수집-저장 과정의 트랜잭션 관리 강화 (All or Nothing)
  * [x] 실패 시 보상 트랜잭션(Rollback) 로직 구현
  * [x] Ingestion Failure Rate 1% 미만 달성

* [x] **Spec 077: Phase 8 Documentation & Archive**
  * [x] Phase 8 완료 사항 아카이브 및 백로그 정리
  * [x] Constitution 및 Agent Guide 업데이트 (Quality Standard)
  * [x] README 현황 최신화
