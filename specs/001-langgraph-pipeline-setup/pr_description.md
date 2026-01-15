## 1. Summary
LangGraph 기반의 데이터 수집 파이프라인 기초 아키텍처를 수립합니다.
도메인 모델(`Source`, `Chunk`), 상태(`GraphState`), 그리고 기본 워크플로우를 구현합니다.

## 2. Changes
- **Docs**: `specs/`, `docs/tech_stack.md`, `backlog/queue.md` 구조 정립.
- **Domain Layer**: `Source` Pydantic model, `GraphState` TypedDict.
- **Application Layer**: `StateGraph` workflow setup with dummy nodes.
- **Entry Point**: `src/main.py` CLI implementation.

## 3. Verification
- `pytest tests/unit` 통과.
- `pytest tests/integration` 통과.
- `uv run python -m src.main` 실행 확인.
