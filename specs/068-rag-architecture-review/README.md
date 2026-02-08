# Spec 068: RAG System Architecture Review

> **목적**: RAG 시스템의 근본적인 아키텍처 문제를 진단하고 개선 방향을 제시합니다.

---

## 📚 문서 구조

이 Spec은 3개의 핵심 문서로 구성되어 있습니다:

### 1️⃣ [spec.md](./spec.md) - 전체 개요 및 분석
**읽는 데 걸리는 시간**: 15~20분

**내용**:
- 배경 및 문제 정의
- RAG 3계층 아키텍처 분석 (Retrieval/Orchestration/LLM Layer)
- 클린 아키텍처 + DDD 위반 사항
- Ingestion 파이프라인 설계 결함
- 프롬프트 편향 및 독소조항

**누구를 위한 문서인가**: 
- 시스템 전반의 문제점을 이해하고 싶은 분
- 아키텍처 개선 방향성을 파악하고 싶은 분

---

### 2️⃣ [root_cause_analysis.md](./root_cause_analysis.md) - 근본 원인 분석
**읽는 데 걸리는 시간**: 25~30분

**내용**:
- **5 Whys 기법**으로 각 문제의 근본 원인 추적
- 실제 **코드 증거** 제시 (파일명, 라인 번호 포함)
- **영향도 분석** (Critical/High/Medium/Low)
- **공통 패턴** 도출 (증상 치료 개발, 테스트 데이터 부재 등)

**주요 Issue**:
- 🔴 **Issue #1**: Ingestion Data Consistency (좀비 데이터)
- 🟠 **Issue #2**: Intent Classifier Prompt Bias
- 🟠 **Issue #3**: Reranker의 독소조항 (PENALTY Rule)
- 🟡 **Issue #4**: Clean Architecture 경계 모호
- 🟢 **Issue #5**: Semantic Chunking 미적용

**누구를 위한 문서인가**:
- 각 문제가 **왜** 발생했는지 깊이 이해하고 싶은 분
- 비슷한 문제의 재발을 방지하고 싶은 분
- 코드 리뷰를 통해 실제 증거를 확인하고 싶은 분

---

### 3️⃣ [recommendations.md](./recommendations.md) - 개선 권장사항
**읽는 데 걸리는 시간**: 20~25분

**내용**:
- **3단계 개선 로드맵** (Quick Wins → Core Improvements → Major Refactoring)
- **우선순위 매트릭스** (Impact vs Effort)
- **구체적인 코드 예시** (Before/After)
- **측정 지표** (Success Metrics)
- **프로세스 개선** (Constitution/Agent.md 업데이트 제안)

**Phase 1: Quick Wins (1주 내)**:
- Task 1.1: Reranker 독소조항 제거 (1일)
- Task 1.2: Prompt Test Dataset 구축 (2일)
- Task 1.3: ChromaDB Upsert 로직 (1일)

**Phase 2: Core Improvements (2~3주)**:
- Task 2.1: Deduplication Service 완성 (5일)
- Task 2.2: Fuzzy Filter Matching (3일)
- Task 2.3: LLMInterface 이동 (2일)

**Phase 3: Major Refactoring (4~6주)**:
- Task 3.1: RAG Graph → Application Layer (10일)
- Task 3.2: Saga Pattern for Ingestion (10일)

**누구를 위한 문서인가**:
- **실제 개선 작업을 시작**하고 싶은 분
- 우선순위 결정에 도움이 필요한 분
- 코드 샘플을 보고 구현 방향을 파악하고 싶은 분

---

## 🎯 어떤 순서로 읽어야 하나요?

### 빠르게 훑어보고 싶다면 (10분)
1. [spec.md](./spec.md) - "문제점" 섹션만 읽기
2. [recommendations.md](./recommendations.md) - "Phase 1: Quick Wins" 섹션만 읽기

### 전체 맥락을 이해하고 싶다면 (60분)
1. [spec.md](./spec.md) - 처음부터 끝까지 (15분)
2. [root_cause_analysis.md](./root_cause_analysis.md) - Issue #1 ~ #3 집중 (20분)
3. [recommendations.md](./recommendations.md) - Phase 1 ~ 2 집중 (25분)

### 깊이 있게 분석하고 싶다면 (90분+)
1. [spec.md](./spec.md) 완독 (20분)
2. [root_cause_analysis.md](./root_cause_analysis.md) 완독 + 코드 확인 (40분)
3. [recommendations.md](./recommendations.md) 완독 (30분)
4. 실제 코드베이스와 비교하며 검증

---

## 📊 핵심 발견 사항 (TL;DR)

### 🔴 최우선 문제 (Critical Issue)

**RAG 3-Layer Architecture의 개념과 코드 괴리**
- **문제**: 문서에는 Brain/Orchestration/Retrieval 3-Layer가 명시되어 있으나, 실제 코드는 **모든 Layer가 한 클래스(`RAGNodes`, 774 lines)에 혼재**
- **영향**: 
  - 새 개발자는 "3-Layer 디자인"을 코드에서 전혀 찾을 수 없음
  - Layer별 독립 테스트 불가능
  - Brain Layer 로직을 다른 파이프라인에서 재사용 불가
- **해결**: 15일 대규모 리팩토링 (Task 3.0)
  - `app/domain/rag/brain/` - Brain Layer 분리
  - `app/application/rag/orchestration/` - Orchestration Layer 분리
  - `app/infrastructure/rag/retrieval/` - Retrieval Layer 분리

---

### 근본 원인 (Root Causes)
1. **증상 치료 개발 패턴**: 문제 발생 → 긴급 수정, 근본 원인은 미해결
2. **테스트 데이터 부재**: 프롬프트, Integration Test의 표준 벤치마크 없음
3. **아키텍처 경험 부족**: Clean Architecture 이론은 알지만 실전 적용 미숙
4. **실험 프로세스 부재**: POC 없이 Full Implementation 시도 → 부담 → 미루기

### 가장 위험한 문제 (Critical Issues)
1. 🔴 **Ingestion Data Consistency**: Neo4j ↔ ChromaDB 불일치 ("좀비 데이터")
2. 🔴 **Saga Pattern 부재**: Transaction Guarantee 없음

### 빠르게 해결 가능한 문제 (Quick Wins)
1. Reranker 독소조항 제거 (1일, Recall +10%)
2. Prompt Test Dataset 구축 (2일, 품질 검증 인프라)
3. ChromaDB Upsert (1일, 중복 저장 방지)

---

## 🚀 다음 단계 (Next Steps)

### 사용자 리뷰 필요 사항
- [ ] 문제 분석에 동의하시나요?
- [ ] 우선순위 (P0 → P1 → P2)에 동의하시나요?
- [ ] Quick Wins 3개 Task를 승인하시나요?

### 즉시 착수 가능한 작업
승인받으면 바로 시작할 수 있는 Task:
1. **Reranker 독소조항 제거** (Spec 069)
2. **Prompt Test Dataset 구축** (Spec 071의 일부)
3. **ChromaDB Upsert** (Small Refactoring, Spec 불필요)

### 추가 논의 필요 사항
- **Deduplication Strategy**: 어떤 것을 우선 구현할지?
- **Saga Pattern**: Transaction Guarantee가 필수인지?
- **Refactoring 타이밍**: 언제 시작할지?

---

## 📖 참고 자료

### 관련 Specs
- [Spec 033](../033-langgraph-state-management/spec.md) - LangGraph State Management
- [Spec 034](../034-rag-pipeline-recovery/spec.md) - RAG Pipeline Recovery
- [Spec 043](../043-robust-ingestion/spec.md) - Robust Ingestion
- [Spec 048](../048-rag-precision/spec.md) - RAG Precision (Reranker 도입)
- [Spec 065](../065-semantic-deduplication/spec.md) - Semantic Deduplication
- [Spec 067](../067-advanced-reranking/spec.md) - Advanced Reranking

### Architecture Docs
- [docs/architecture/rag_pipeline.md](../../docs/architecture/rag_pipeline.md) - RAG 3-Layer 패턴
- [docs/architecture/architecture.md](../../docs/architecture/architecture.md) - Clean Architecture 원칙

### Code References
주요 문제가 있는 파일:
- `app/domain/services/intent_classifier.py` - 프롬프트 편향
- `app/domain/services/prompts/reranker.py` - 독소조항
- `app/infrastructure/repositories/rag_nodes.py` - 계층 혼재
- `app/infrastructure/repositories/chroma.py` - 중복 저장 이슈

---

## ❓ FAQ

### Q1: 왜 이 분석이 필요한가요?
**A**: 지금까지 67개의 Spec을 진행하면서 퀄리티 이슈가 반복되고 있습니다. **증상만 치료**하면 같은 문제가 다른 곳에서 재발합니다. 근본 원인을 파악해야 효율적인 개선이 가능합니다.

### Q2: 모든 권장사항을 다 해야 하나요?
**A**: 아닙니다. **Quick Wins (Phase 1)**만 먼저 진행해도 큰 효과를 볼 수 있습니다. Phase 2, 3은 시간과 우선순위에 따라 선택적으로 진행하면 됩니다.

### Q3: 예상 소요 시간은?
**A**:
- Phase 1 (Quick Wins): **1주**
- Phase 2 (Core Improvements): **2~3주**
- Phase 3 (Major Refactoring): **4~6주**

단, 모두 병렬로 진행할 필요는 없습니다.

### Q4: 코딩 없이 리뷰만 하는 건가요?
**A**: 이 Spec 자체는 **분석 및 제안**만 포함합니다. 실제 구현은 각 Phase의 Task를 별도 Spec으로 승격하여 진행합니다 (예: Spec 069, 070, ...).

### Q5: 프로세스 개선 제안은 어떻게 되나요?
**A**: `recommendations.md`의 마지막 섹션에서 **Constitution.md/Agent.md 업데이트** 제안이 있습니다. 승인하시면 적용하겠습니다.

---

## 📝 변경 이력

- **2026-02-08**: Spec 068 최초 작성 (분석 문서 3개 완성)

---

> **Note**: 이 Spec은 코드 변경을 포함하지 않습니다. 순수 **분석 및 제안** 문서입니다.
