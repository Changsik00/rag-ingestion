# Implementation Plan: Spec-021 (Advanced Backtracking)

## 📋 Branch Strategy
- `feature/spec-021-logic-resolver`

## 🛑 User Review Required
- **Testing Scope**: 단순히 Core Logic만 테스트하는 것이 아니라, "상태 변화(Transition)"와 "프롬프트 변화(Mutation)"를 검증하는 시나리오 테스트가 필수적입니다.
- **Mocking Strategy**: Graph 전체를 돌리는 통합 테스트에서는 `LLM`을 Mocking하여 특정 회차(`attempt_number`)마다 다른 응답을 주도록 설정해야 합니다.

## 🎯 Core Strategy
- **Framework First**: 4가지 전략과 예측형 모델을 모두 담을 수 있는 유연한 State 설계.
- **Smart Feedback**: 단순 에러 메시지가 아닌, **수정 대상(Fields)과 전략(Strategy)**을 포함한 고차원 피드백 전달.

## 📂 Proposed Changes

### [Domain Layer] Advanced State Design

#### [MODIFY] `app/domain/ingestion/state.py`
- **Updated Models**:
    - `StrategyType` Enum (CORRECTION, RELAXATION, REINTERPRETATION, DECOMPOSITION).
    - `ValidationFeedback`: Add `target_fields: list[str] | None` for **Partial Retry**.
    - `IngestionState`: Add `predicted_category` (for Future Predictive), `active_constraints`.

### [Infrastructure Layer] Intelligent Nodes

#### [MODIFY] `nodes.py` (Smart Validator & Extractor)
- **Validator**:
    - Validation 실패 시, 실패한 필드명을 `target_fields`에 담아 반환.
- **Extractor**:
    - `current_strategy == CORRECTION`: `target_fields`가 있으면 "Only fix these fields: {fields}" 프롬프트 생성 (**Partial Retry**).
    - `current_strategy == RELAXATION`: "Ignore strict formatting rules" 프롬프트 추가.

#### [NEW] `logic.py` (Meta-Reasoner)
- **Strategy Selector**:
    - 1차 실패 (Validation Error): -> `CORRECTION` (Partial Retry).
    - 2차 실패 (Same Error): -> `RELAXATION` (Switch Strategy).
    - Schema Mismatch: -> `REINTERPRETATION` (Future Mock).

#### [MODIFY] `graph.py`
- Conditional Edge 연결: `validate` -> `logic` -> `extract`.

## 🧪 Verification Plan

### Automated Tests
#### 1. Unit Tests (Logic & State)
```bash
# 전략 선택 로직 검증
uv run pytest tests/unit/infrastructure/brain/test_logic_selector.py
# 프롬프트 생성 로직 검증 (Partial Retry 반영 여부)
uv run pytest tests/unit/infrastructure/brain/test_prompt_mutation.py
```

#### 2. Integration Tests (Scenarios)
```bash
uv run pytest tests/integration/test_backtracking_scenarios.py
```
- **Scenario A: Partial Retry**
    - `Attempt 1`: Title 누락 (Fail)
    - `Logic`: Select `CORRECTION`
    - `Attempt 2`: Title만 생성 요청 (Prompt Check) -> Success
- **Scenario B: Relaxation**
    - `Attempt 1`: Entities 과다 (Fail)
    - `Attempt 2`: Entities 과다 (Fail)
    - `Logic`: Select `RELAXATION`
    - `Attempt 3`: 완화된 룰로 성공
- **Scenario C: Max Retry**
    - 3회 연속 실패 -> `FAIL` 상태로 종료 확인

### Manual Verification
- **Trace Analysis**: Log에서 `Strategy Switching` (STANDARD -> CORRECTION -> RELAXATION) 로그 확인.
