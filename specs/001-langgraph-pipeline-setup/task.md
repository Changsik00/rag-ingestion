# Task: LangGraph Pipeline Setup (Strict Loop)

- [x] **Task 0: Environment & Docs**
    - [x] `docs/tech_stack.md` creation & `README.md` update (Commit: `1da1651`)
    - [x] `uv init` execution (Project Initialization)
    - [x] `uv add` execution (Dependencies: fastapi, langgraph, etc.)
- [x] **Task 1: Domain Layer** - `Source` & `Chunk` 모델 구현 (`src/domain/models/source.py`)
    - [x] Unit Test 작성/수정 (`tests/unit/test_source.py`)
    - [x] 코드 구현
    - [x] 테스트 검증 (Pass)
- [x] **Task 2: Domain Layer** - `GraphState` 구현 (`src/domain/state.py`)
    - [x] Unit Test 작성/수정
    - [x] 코드 구현
    - [x] 테스트 검증 (Pass)
- [x] **Task 3: Applicaton Layer** - Dummy Nodes 구현 (`src/application/nodes/mock_nodes.py`)
- [x] **Task 4: Applicaton Layer** - Workflow 구현 (`src/application/workflow.py`)
- [x] **Task 5: Entry Point** - Main 진입점 구현 (`src/main.py`)
    - [x] Integration Test 작성 (`tests/integration/test_pipeline_execution.py`)
    - [x] CLI 실행 검증 (`uv run python -m src.main`)
