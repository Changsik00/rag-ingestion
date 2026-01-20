# feat(spec-021): logic resolver & polymorphic backtracking

## 📋 Summary
기존의 단순 선형(Linear) Ingestion 파이프라인을 LangGraph의 Conditional Edges를 활용한 **지능형 백트래킹(Polymorphic Backtracking)** 구조로 고도화하였습니다.
단순히 재시도(Retry)하는 것이 아니라, **실패 원인에 따라 적절한 대응 전략(Strategy)을 선택**하여 LLM의 성공률을 높이는 것이 핵심입니다.

## 🎯 Key Review Points
### 1. Polymorphic State Architecture (`app/domain/ingestion/state.py`)
- **StrategyType**: 4가지 핵심 전략을 Enum으로 정의했습니다.
  - `CORRECTION`: 단순 실수 교정 (Reasoning Retry)
  - `RELAXATION`: 엄격한 규칙 완화 (Constraint Re-evaluation)
  - `REINTERPRETATION`: (Future) 스키마 변경
  - `DECOMPOSITION`: (Future) 문서 쪼개기
- **ValidationFeedback**: `target_fields`를 추가하여, LLM에게 "이 필드만 고쳐줘"라고 명확히 지시할 수 있게 했습니다 (Partial Retry).

### 2. Logic Resolver (`app/infrastructure/brain/logic.py`)
- **Meta-Reasoner**: 현재 재시도 횟수(`retry_count`)와 에러 내역(`feedbacks`)을 분석하여 다음 전략을 결정합니다.
  - 1차 실패 시: `CORRECTION` 모드 진입.
  - 2회 이상 반복 실패 시: `RELAXATION` 모드 진입 (규칙 완화).

### 3. Dynamic Extractor (`app/infrastructure/brain/nodes.py`)
- **Strategy-Aware Prompting**: 현재 전략에 따라 시스템 프롬프트를 동적으로 변경합니다.
  - `CORRECTION` 모드: 이전 에러 메시지와 타겟 필드를 포함한 "비평(Critic)" 프롬프트 주입.
  - `RELAXATION` 모드: "규칙을 완화해도 좋다"는 지시 사항 주입.

## 🧪 Verification
### Automated Tests
#### Unit Tests
- `tests/unit/domain/ingestion/test_state_advanced.py`: State 모델 및 전이 로직 검증.
- `tests/unit/infrastructure/brain/test_logic_selector.py`: 에러 패턴별 전략 매핑 검증.
- `tests/unit/infrastructure/brain/test_prompt_mutation.py`: 전략별 프롬프트 변경 여부 검증.

#### Integration Tests (BDD Scenarios)
- **File**: `tests/integration/bdd/test_logic_resolver.py`
  - `test_should_trigger_correction_strategy_on_partial_failure`: 부분 실패 시 교정 전략 동작 확인.
  - `test_should_trigger_relaxation_strategy_on_repeated_failure`: 반복 실패 시 완화 전략 동작 확인.
  - `test_should_maintain_standard_strategy_if_no_feedback`: 피드백 부재 시 기본 전략 유지 확인.
  - `test_should_suggest_relaxation_on_max_retry_attempt`: Max Retry 도달 시의 동작 확인.

```bash
uv run pytest tests/integration/bdd/test_logic_resolver.py
```

## 📦 Files Changed
- **Domain**: `app/domain/ingestion/state.py` (StrategyType, ValidationFeedback)
- **Infrastructure**:
  - `app/infrastructure/brain/logic.py` (New: Strategy Selection)
  - `app/infrastructure/brain/nodes.py` (Modified: Dynamic Prompting)
  - `app/infrastructure/brain/graph.py` (Modified: Conditional Edges)
- **Tests**: `tests/integration/bdd/test_logic_resolver.py` (New: BDD Scenarios)

## ✅ Definition of Done
- [x] 4가지 전략(StrategyType) 정의 및 State 반영
- [x] Logic Resolver 구현 (에러 -> 전략 매핑)
- [x] Partial Retry를 위한 Dynamic Prompting 구현
- [x] BDD 시나리오 테스트(Partial Failure, Repeated Failure) 통과
