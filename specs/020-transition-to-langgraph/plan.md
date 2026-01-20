# Implementation Plan: Spec 020

## 📋 Branch Strategy
- `feature/spec-020-langgraph-transition`

## 🛑 User Review Required
- **Breaking Change**: 내부적으로 `LangChainAdapter`가 `LangGraphAdapter`로 교체되지만, `Port` 인터페이스를 유지하여 영향도를 최소화할 예정입니다.
- **Dependency**: `langgraph` 라이브러리 추가가 필요합니다.

## 🎯 Core Strategy
- **State Pattern**: 모든 데이터 흐름을 `IngestionState`라는 단일 진실 공급원(Single Source of Truth)으로 관리합니다.
- **Graph as a Service**: Graph를 컴파일(`compile()`)하여 `Runnable`처럼 사용, 기존 코드와의 호환성을 유지합니다.
- **Incremental Refactoring**:
    1.  State 정의
    2.  Node 구현 (기존 Logic 이식)
    3.  Graph 구성
    4.  Adapter 교체

## 📂 Proposed Changes

### [Documentation]
#### [NEW] `docs/architecture_decisions/001_dag_to_graph_transition.md`
- Architecture Decision Record (ADR) explaining the shift from Linear DAG to Stateful Graph.
- Includes Mermaid diagrams comparing both approaches.

#### [MODIFY] `docs/architecture.md`
- Add reference to the new ADR.

### [Library]
#### [NEW] `pyproject.toml`
- `langgraph` 의존성 추가

### [Domain Layer]
#### [NEW] `app/domain/ingestion/state.py`
```python
from typing import TypedDict, List, Optional

class IngestionState(TypedDict):
    original_url: str
    raw_content: str
    metadata: dict
    extracted_entities: List[dict]
    # ...
```

### [Infrastructure Layer]
#### [NEW] `app/infrastructure/brain/nodes.py`
- `extract_metadata_node(state: IngestionState) -> dict`
- `validate_content_node(state: IngestionState) -> dict`

#### [NEW] `app/infrastructure/brain/graph.py`
- `build_ingestion_graph() -> CompiledGraph`

#### [MODIFY] `app/infrastructure/brain/adapter.py`
- 기존 `LangChainAdapter`를 `LangGraphAdapter`로 리네임/교체
- `StateGraph`를 주입받아 실행

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests (New Nodes & State)
uv run pytest tests/unit/test_ingestion_state.py
uv run pytest tests/unit/test_graph_nodes.py

# Integration Tests (Regression)
uv run pytest tests/integration/bdd/test_success_flows.py
```

### Manual Verification
1.  서버 구동: `uv run uvicorn app.main:app --reload`
2.  API 호출: `POST /ingest/web`
3.  로그 확인: LangGraph의 Node 실행 로그(`Extract` -> `Save`)가 순차적으로 찍히는지 확인.
