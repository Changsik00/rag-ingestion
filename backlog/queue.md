# 📋 Master Project Backlog (backlog/queue.md)

이 문서는 프로젝트의 전체 여정과 실행 우선순위를 관리하는 마스터 대시보드입니다. 모든 작업은 [`constitution.md`](../docs/constitution.md)의 **Backlog Law**를 준수하며, 사용자의 승인을 통해 **Spec**으로 승격되어 실행됩니다.

> **Note**: 완료된 작업(Phase 1~7)은 [🗄️ Archive](archive.md)로 이동되었습니다.

---

## 🏗️ Phase 8: Architecture & Quality Foundation

> **목표**: RAG 시스템의 근본적인 아키텍처 문제를 해결하고 품질 검증 인프라를 구축한다.  
> **기반**: [**Spec 068: RAG System Architecture Review**](../specs/068-rag-architecture-review/README.md) 분석 결과  
> **기간**: 8~10주 (순차적 진행)
> **현재 상태**: Spec 075 (Brain Layer Refactoring) 진행 중

### 📊 Phase 8 Overview

[Spec 068](../specs/068-rag-architecture-review/spec.md)에서 분석한 4대 문제 영역:

1. 🔴 **RAG 3-Layer 코드 구조 괴리** ([분석](../specs/068-rag-architecture-review/spec.md#10--근본적-구조-문제-개념과-코드의-괴리))
2. 🟠 **프롬프트 편향 및 독소조항** ([분석](../specs/068-rag-architecture-review/root_cause_analysis.md#-high-issue-2-intent-classifier-prompt-bias))
3. 🟠 **Ingestion 파이프라인 설계 결함** ([분석](../specs/068-rag-architecture-review/spec.md#3-ingestion-파이프라인-설계-결함))
4. 🟡 **Clean Architecture 위반** ([분석](../specs/068-rag-architecture-review/spec.md#2-클린-아키텍처--ddd-위반-사항))

---

### 📋 Spec List

* [x] **Spec 069: Reranker Prompt Optimization** (P0, 1일) 🚀 **Quick Win**
  * **Goal**: Reranker 독소조항 제거 및 Context-Aware 프롬프트로 교체
  * **근거**: [Root Cause #3](../specs/068-rag-architecture-review/root_cause_analysis.md#-high-issue-3-reranker의-독소조항-penalty-rule)
  * **Tasks**:
    - [x] `PENALTY` 규칙 제거, Context-Aware 평가 기준 추가
    - [x] `reranker_v2.py` 작성 및 Feature Flag 추가
    - [x] A/B 테스트 10개 질문 실행
    - [x] Recall +10% 확인 후 v2 기본값 적용
  * **Expected Impact**: Over-filtering 해결, Recall 향상

* [x] **Spec 070: Prompt Quality Testing Framework** (P0, 2일) 🚀 **Quick Win** → **PR #76**
  * **Goal**: Intent Classifier 테스트 케이스 50개 구축 및 자동 검증
  * **근거**: [Root Cause #2](../specs/068-rag-architecture-review/root_cause_analysis.md#-high-issue-2-intent-classifier-prompt-bias)
  * **Tasks**:
    - [x] 다양한 도메인 테스트 케이스 50개 작성 (YAML)
    - [x] Pytest 자동 검증 스크립트
    - [x] 현재 Accuracy Baseline 측정 (89.3%)
    - [ ] CI/CD에 Prompt Quality Test 추가 (Skipped - .github/workflows 없음)
  * **Expected Impact**: "어쩌다 어른" 편향 해결 ✅
  * **Note**: Baseline Accuracy 89.3% (목표 80% 초과). 편향 해소 확인 완료.

* [x] **Spec 071: ChromaDB Upsert Logic** (P1, 1일) 🚀 **Quick Win**
  * **Goal**: 중복 저장 방지 (`add` → `upsert`)
  * **근거**: [Root Cause #1](../specs/068-rag-architecture-review/root_cause_analysis.md#-critical-issue-1-ingestion-data-consistency-좀비-데이터)
  * **Tasks**:
    - [x] ChromaDB `upsert` 메서드 적용
    - [x] 동일 문서 2번 수집 시 중복 생성 테스트
    - [x] Integration Test 추가
  * **Expected Impact**: 중복 저장 방지
  * **Note**: 완료 (2026-02-09). PR 머지 완료. ✅

* [x] **Spec 072: Robust Deduplication Framework** (P0, 5일) 🔄 **Planning 진행 중**
  * **Goal**: 4가지 Strategy (ID/Metadata/TTL/Contents) 실제 구현
  * **근거**: [Spec 068 - Ingestion 중복 처리](../specs/068-rag-architecture-review/spec.md#32-중복-처리-deduplication-설계-결함)
  * **상세 계획**: [Task 2.1](../specs/068-rag-architecture-review/recommendations.md#task-21-deduplication-service-완성-)
  * **Tasks**:
    - [x] `DeduplicationStrategy` Protocol 정의
    - [x] 4가지 Strategy 클래스 구현
    - [x] Factory Pattern 적용
    - [x] Ingestion Graph에 `check_duplicate` Node 추가
    - [x] Admin UI Strategy 선택 기능
  * **Expected Impact**: 중복 수집 방지, 불필요한 재수집 감소
  * **Note**: Planning 완료 (2026-02-09). [spec.md](../specs/072-robust-deduplication-framework/spec.md), [plan.md](../specs/072-robust-deduplication-framework/plan.md), [task.md](../specs/072-robust-deduplication-framework/task.md) 작성 완료. **User Plan Accept 대기 중**.

* [x] **Spec 073: Fuzzy Filter Matching** (P1, 3일) ✅ **PR 제출 (#79)**
  * **Goal**: Source Filter Semantic Similarity 기반 매칭
  * **근거**: [Spec 068 - Filter 강제성의 함정](../specs/068-rag-architecture-review/spec.md#13-retrieval-layer-memorybody)
  * **상세 계획**: [Task 2.2](../specs/068-rag-architecture-review/recommendations.md#task-22-fuzzy-filter-matching-)
  * **Tasks**:
    - [x] `FilterMatcher` Service 구현
    - [x] "Claude" ↔ "claude" 매칭 테스트
    - [x] RAG Graph `route_decision` 통합
  * **Expected Impact**: Exact Match 실패 문제 해결
  * **PR**: https://github.com/Changsik00/rag-ingestion/pull/79
  * **완료 날짜**: 2026-02-09

* [x] **Spec 074: LLMInterface Clean Architecture Compliance** (P1, 2일)
  * **Goal**: `LLMInterface`를 Domain Layer로 이동
  * **근거**: [Spec 068 - Domain Service LLM 의존성](../specs/068-rag-architecture-review/spec.md#22-domain-service의-llm-의존성-문제)
  * **상세 계획**: [Task 2.3](../specs/068-rag-architecture-review/recommendations.md#task-23-llminterface-이동-clean-architecture-)
  * **Tasks**:
    - [x] `app/application/interfaces/llm.py` → `app/domain/interfaces/llm.py`
    - [x] 모든 Import 경로 수정
    - [x] Dependency Rule 검증 스크립트
  * **Expected Impact**: Clean Architecture 준수, Dependency Rule 위반 해소

* [/] **Spec 075: RAG 3-Layer Code Structure Refactoring** ⭐⭐⭐⭐ (P0, 15일) 🔄 **Execution 진행 중**
  * **Goal**: 개념적 3-Layer를 실제 코드 구조에 반영
  * **근거**: [Spec 068 - 1.0 근본적 구조 문제](../specs/068-rag-architecture-review/spec.md#10--근본적-구조-문제-개념과-코드의-괴리)
  * **Core Problem**: 
    - `app/infrastructure/ai/rag_nodes.py` (774 lines)에 Brain/Orchestration/Retrieval 혼재
    - 문서 3-Layer 디자인이 코드에서 전혀 안 보임
  * **상세 계획**: [Task 3.0 - Week별 계획](../specs/068-rag-architecture-review/recommendations.md#task-30-rag-3-layer-code-structure-refactoring-)
  * **Tasks**:
    - [ ] **Week 1**: Brain Layer 분리 (`app/domain/rag/brain/`)
    - [ ] **Week 2**: Retrieval Layer 분리 (`app/infrastructure/rag/retrieval/`)
    - [ ] **Week 3**: Orchestration Layer 분리 (`app/application/rag/orchestration/`)
    - [ ] **Week 4**: LangGraph Integration & E2E Test
    - [ ] `rag_nodes.py` (774 lines) 삭제
    - [ ] Architecture 문서 업데이트 및 ADR 작성
  * **Expected Impact**: 
    - 아키텍처 문서 ↔ 코드 일치
    - Layer별 독립 테스트
    - Brain Layer 재사용

* [ ] **Spec 076: Ingestion Transaction Integrity (Saga Pattern)** (P3, 10일)
  * **Goal**: Neo4j ↔ ChromaDB Transaction Guarantee
  * **근거**: [Spec 068 - Ingestion State Management](../specs/068-rag-architecture-review/spec.md#33-ingestion-state-management-부족)
  * **상세 계획**: [Task 3.2](../specs/068-rag-architecture-review/recommendations.md#task-32-saga-pattern-for-ingestion-)
  * **Tasks**:
    - [ ] `IngestionSaga` Orchestrator 구현
    - [ ] Audit Logging 인프라
    - [ ] Compensation Logic (Rollback)
    - [ ] Admin UI Saga 실패 조회
  * **Expected Impact**: "좀비 데이터" 방지

* [ ] **Constitution.md 업데이트: Prompt Quality Standard**
  * **근거**: [Spec 068 - Process Improvements](../specs/068-rag-architecture-review/recommendations.md#-프로세스-개선-constitutionagentmd-업데이트)
  * **Tasks**:
    - [ ] 최소 20개 테스트 케이스 검증 규칙
    - [ ] Prompt Versioning 규칙
    - [ ] Hard-coded Examples 금지

* [ ] **Agent.md 업데이트: Research Spec 카테고리**
  * **근거**: [Spec 068 - Process Improvements](../specs/068-rag-architecture-review/recommendations.md#2-research-spec-카테고리-추가)
  * **Tasks**:
    - [ ] Research Spec Definition of Done
    - [ ] Trade-off 측정 중심 프로세스

---

## 🎯 Phase 8 Success Metrics

### Quick Wins (Spec 069~071)
- [ ] Reranker Recall +10% 이상
- [ ] Intent Classification Accuracy Baseline 측정
- [ ] ChromaDB 중복 저장 0건

### Core Improvements (Spec 072~074)
- [ ] Deduplication Skip Rate 측정
- [ ] Filter Matching Success Rate 95% 이상
- [ ] Dependency Rule Violation 0건

### Major Refactoring (Spec 075~076)
- [ ] Clean Architecture Compliance 100%
- [ ] RAG 3-Layer 코드 ↔ 문서 일치
- [ ] Layer별 Unit Test Coverage 80% 이상
- [ ] Ingestion Failure Rate < 1%

---

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