feat(spec-023): reasoning context and failure analysis

## 📋 Summary
본 PR은 Ingestion Pipeline의 Backtracking 메커니즘을 "단순 반복(Blind Retry)"에서 **"원인 분석 후 전략적 재시도(Reasoning Retry)"**로 전환합니다.
기존 시스템은 실패 시 무조건 다음 전략을 시도했으나, 변경된 시스템은 실패 원인을 분석(`analyze_failure`)하고 그 맥락(`Reasoning Context`)을 다음 시도에 주입하여 LLM이 스스로 오류를 수정하도록 유도합니다.

**Before:**
- 실패 -> 횟수 증가 -> 전략 변경(무작위/순차) -> 재시도 (LLM은 왜 실패했는지 모름)

**After:**
- 실패 -> **원인 분석(Analyze)** -> **가설 수립(Hypothesis)** -> 전략 변경 -> 재시도 (LLM에게 "이전에는 X 때문에 실패했어"라고 알려줌)

## 🎯 Key Review Points
1.  **State 구조 확장 (`app/domain/ingestion/state.py`)**:
    - `FailureHypothesis`: 실패 원인(cause), 설명(description), 잘못된 전제(invalid_assumptions) 저장.
    - `BacktrackingContext`: 전체 사고 과정을 추적하는 컨테이너.
    - *기존 로직에 영향을 주지 않도록 Optional 필드로 추가되었습니다.*

2.  **Failure Analysis Node (`app/infrastructure/brain/nodes.py`)**:
    - `analyze_failure` 메서드 추가.
    - 현재는 **Rule-based**로 `last_feedback`을 분석하여 `missing_info` 또는 `validation_error` 가설을 생성합니다.
    - 향후 LLM 기반의 심층 분석으로 확장이 용이하도록 구조화했습니다.

3.  **Graph Flow 변경 (`app/infrastructure/brain/graph.py`)**:
    - `Validate`(Fail) -> `Analyze` -> `Logic` -> `Extract` 순서로 엣지를 재구성했습니다.

## 🧪 Verification

### Automated Tests
```bash
# 1. State & Logic Unit Tests
uv run pytest tests/unit/test_reasoning_state.py
uv run pytest tests/unit/test_analysis_node.py
uv run pytest tests/unit/test_prompt_injection.py

# 2. Integration Tests (BDD)
# 전체 재시도 루프(실패 -> 분석 -> 프롬프트 주입 -> 재시도) 검증
uv run pytest tests/integration/bdd/test_reasoning_flow.py

# 3. Full Suite
uv run pytest
```

### Manual Verification
- `scripts/verify_hitl_real.py` (Icebox) 등을 통해 실제 LLM이 주입된 Context에 반응하는지 확인할 수 있습니다.

## 📦 Files Changed

### 🆕 New Files
- `tests/unit/test_reasoning_state.py`: State 타입 정의 테스트
- `tests/unit/test_analysis_node.py`: 분석 노드 로직 테스트
- `tests/unit/test_prompt_injection.py`: 프롬프트 주입 테스트
- `tests/integration/bdd/test_reasoning_flow.py`: BDD 통합 테스트

### 🛠 Modified Files
- `app/domain/ingestion/state.py`: `FailureHypothesis`, `BacktrackingContext` 추가
- `app/infrastructure/brain/nodes.py`: `analyze_failure` 추가, `construct_extraction_prompt` 수정
- `app/infrastructure/brain/graph.py`: Node/Edge 라우팅 변경

## ✅ Definition of Done
- [x] `IngestionState`에 Reasoning Context 관련 필드 정의
- [x] 실패 시 `analyze_failure` 실행 및 `FailureHypothesis` 생성
- [x] 재시도 프롬프트에 실패 원인 주입
- [x] 모든 테스트 통과 (Unit, Integration, Full Suite)
