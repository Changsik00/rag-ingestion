# PR Description: LangGraph Pipeline Setup

## 1. Summary
LangGraph 기반의 데이터 수집 파이프라인 기초 아키텍처를 수립합니다.
도메인 모델(`Source`, `Chunk`), 상태(`GraphState`), 그리고 기본 워크플로우를 구현합니다.

## 2. Changes
- **Domain Layer**: `Source` Pydantic model, `GraphState` TypedDict.
- **Application Layer**: `StateGraph` workflow setup with dummy nodes.
- **Entry Point**: Basic CLI for testing.

## 3. Verification
- `pytest tests/unit` 통과 확인.
- `src/main.py` 실행 시 정상적인 그래프 흐름 출력 확인.
