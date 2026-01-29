# Implementation Plan: Spec-023

## 📋 Branch Strategy
- `feature/023-reasoning-context`

## 🛑 User Review Required
- [x] **State Structure Update**: `IngestionState`에 `backtracking_context` 딕셔너리가 추가됩니다. 디버깅 복잡도가 증가할 수 있습니다.
- [x] **Recall Cost**: `analyze_failure` 단계에서 초기 구현은 Rule-based로 진행하여 비용을 최소화합니다. (LLM 사용 X)

## 🎯 Core Strategy
- **State Expansion**: 단순히 에러 메시지만 남기는 것이 아니라, `FailureHypothesis`(가설)와 `DecisionTrace`(의사결정)를 상태에 저장하여 "사고의 연속성"을 보장합니다.
- **Explicit Analysis Phase**: `Validation` 실패 후 `Resolve`로 바로 가지 않고, `Analyze` 단계를 거쳐 실패 원인을 명확히 규명한 뒤 전략을 수립합니다.
- **Prompt Injection**: LLM에게 "넌 실패했어"라고만 하는 대신, "이러이러한 이유로 실패했으니, 이렇게 관점을 바꿔서 다시 해봐"라고 구체적인 가이드를 제공합니다.

## 📂 Proposed Changes

### Domain Layer

#### [MODIFY] `app/domain/ingestion/state.py`
- `FailureHypothesis`, `QuestionInterpretation`, `DecisionTrace` TypedDict 정의
- `IngestionState`에 `backtracking_context` 필드 추가

### Infrastructure Layer

#### [MODIFY] `app/infrastructure/brain/nodes.py`
- `analyze_failure` 메서드 추가 (Rule-based logic)
- `construct_extraction_prompt` 수정 (Reasoning Context 주입 로직 추가)

### Graph Layer

#### [MODIFY] `app/infrastructure/brain/graph.py`
- `analyze_failure` 노드 등록
- Conditional Edge 수정: `validate_content` (Fail) -> `analyze_failure` -> `resolve_logic` -> `extract_metadata`

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests (State & Prompt Logic)
uv run pytest tests/unit/test_reasoning_state.py
uv run pytest tests/unit/test_prompt_injection.py

# Integration Tests (BDD Flow)
uv run pytest tests/integration/bdd/test_reasoning_flow.py
```

### Manual Verification
1. `scripts/verify_hitl_real.py` (Icebox)를 활용하여 실제 LLM이 실패 가설을 인지하고 반응하는지 로그 확인.
