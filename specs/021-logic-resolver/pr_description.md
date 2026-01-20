# feat(spec-021): logic resolver & polymorphic backtracking

## 📋 Summary
기존의 단순 선형(Linear) Ingestion 파이프라인을 LangGraph의 Conditional Edges를 활용한 **지능형 백트래킹(Polymorphic Backtracking)** 구조로 고도화하였습니다.
단순 재시도(Retry)를 넘어, 실패 원인에 따라 **전략(Strategy)**을 수정하며 재시도하는 `Meta-Reasoner` 구조를 도입했습니다.

## 🎯 Key Review Points
1. **Polymorphic State**: 4가지 전략(`Correction`, `Relaxation`, `Reinterpretation`, `Decomposition`)을 수용하는 `StrategyType` 및 `IngestionState` 설계.
2. **Logic Resolver**: 에러 패턴에 따라 최적의 전략을 선택하는 `select_strategy` 로직.
3. **Partial Retry**: 전체 재생성이 아닌, 오류가 발생한 필드(`target_fields`)만 집중 수정하도록 유도하는 프롬프트 전략.

## 🧪 Verification
### Automated Tests
```bash
# Unit Tests (Logic & State)
uv run pytest tests/unit/domain/ingestion/test_state_advanced.py
uv run pytest tests/unit/infrastructure/brain/test_logic_selector.py
uv run pytest tests/unit/infrastructure/brain/test_prompt_mutation.py

# Integration Tests (Backtracking Scenarios)
uv run pytest tests/integration/test_backtracking.py
```

### Manual Verification
- Trace Logs를 통해 `STANDARD` -> `CORRECTION` -> `RELAXATION` 전략 전환 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/infrastructure/brain/logic.py`: 전략 선택(Meta-Reasoner) 로직 구현.
- `tests/unit/infrastructure/brain/test_logic_selector.py`: 전략 선택 단위 테스트.
- `tests/unit/infrastructure/brain/test_prompt_mutation.py`: 프롬프트 변경 단위 테스트.

### 🛠 Modified Files
- `app/domain/ingestion/state.py`: `StrategyType`, `ValidationConstraints`, `ValidationFeedback` 모델 추가.
- `app/infrastructure/brain/nodes.py`: 전략에 따른 동적 프롬프트 생성 로직 추가.
- `app/infrastructure/brain/graph.py`: Conditional Edge 연결.

## ✅ Definition of Done
- [ ] 4가지 전략 Enum 정의 및 State 반영
- [ ] Partial Retry (필드 지정 수정) 프롬프트 동작 확인
- [ ] Strategy Switching (Relaxation 등) 동작 확인
- [ ] 관련 Unit/Integration Test 통과
