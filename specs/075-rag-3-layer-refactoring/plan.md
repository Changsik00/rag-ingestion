# Implementation Plan: Spec 075

## 📋 Branch Strategy
- `feature/spec-075-rag-3-layer-refactoring`

## 🛑 User Review Required
> [!IMPORTANT]
> - **파일 시스템 변경**: `rag_nodes.py` (774 lines) 파일이 완전히 분해되어 삭제될 예정입니다. 이는 현재의 모든 RAG 흐름에 영향을 미칩니다.
> - **의존성 주입 (DI)**: 새로운 컴포넌트들은 `app/main.py` 또는 `Container`에서 의존성 주입 설정이 필요합니다.

## 🎯 Core Strategy

### Architecture Context
이번 3-Layer 리팩토링은 **Clean Architecture** 원칙을 엄격히 준수합니다:
1. **Brain (Domain)**: 순수 비즈니스 로직, 외부 의존성 없음.
2. **Orchestration (Application)**: 워크플로우 정의, 인터페이스 활용.
3. **Retrieval (Infrastructure)**: 검색 및 데이터베이스 접근 구현.

**"Strangler Fig" (교살자 무화과)** 패턴을 적용하여 안전하게 전환합니다:
1. 새로운 디렉토리와 클래스를 먼저 생성합니다.
2. `rag_nodes.py`의 로직을 새로운 클래스로 복사 및 이식합니다 (Copy & Adapt).
3. 새로운 오케스트레이터를 사용하는 `LangGraph`를 정의합니다.
4. 병렬 실행 또는 기능 전환을 검증합니다.
5. 기존 `rag_nodes.py`를 삭제합니다.

### Component Map

| Component | Layer | Purpose |
|:---:|:---|:---|
| `BrainService` | Domain | 의도 분류 (Intent Classification), 쿼리 재작성 (Query Rewriting) |
| `RetrievalService` | Infrastructure | 하이브리드 검색 (Hybrid Search), 리랭킹 실행 (Reranking) |
| `RAGOrchestrator` | Application | LangGraph 노드 정의, 상태 관리 (State Management) |

## 📂 Proposed Changes

### Application Layer

#### [NEW] `app/application/rag/nodes/orchestrator.py`
- `RAGOrchestrator` 클래스 정의.
- LangGraph 시그니처와 일치하는 메서드(`classify_intent`, `retrieve`, `generate_answer`) 구현.

#### [NEW] `app/application/rag/graph.py`
- `RAGOrchestrator`를 사용하는 새로운 그래프 구조 정의.

### Domain Layer

#### [NEW] `app/domain/rag/brain/service.py`
- `BrainService` 클래스.
- 메서드: `classify_intent()`, `rewrite_query()`.

### Infrastructure Layer

#### [NEW] `app/infrastructure/rag/retrieval/service.py`
- `RetrievalService` 클래스.
- 메서드: `hybrid_search()`, `rerank()`.

### Legacy Cleanup

#### [DELETE] `app/infrastructure/ai/rag_nodes.py`
- 모든 기능 이관 후 삭제.

## 🧪 Verification Plan

### Automated Tests
```bash
# Brain Layer 단위 테스트
uv run pytest tests/domain/rag/brain/

# Retrieval Layer 단위 테스트
uv run pytest tests/infrastructure/rag/retrieval/

# Orchestration 통합 테스트
uv run pytest tests/application/rag/
```

### Manual Verification
1. `make run`으로 서버를 시작합니다.
2. `/chat` 엔드포인트에 다양한 의도(일반 질문, 특정 질문 등)로 쿼리를 전송합니다.
3. RAG 프로세스가 에러 없이 완료되는지 확인합니다.
4. LangSmith 트레이스를 통해 각 노드가 올바른 순서로 실행되는지 검증합니다.
