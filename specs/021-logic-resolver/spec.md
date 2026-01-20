# Spec-021: Polymorphic & Advanced Backtracking Framework

## 📋 배경 및 문제 정의 (Background & Problem)
단순 재시도(Level 1)를 넘어, 상황에 맞는 전략을 선택하는 **Polymorphic Backtracking**이 필요합니다.
또한, 비용 효율성을 위해 전체 생성이 아닌 문제 필드만 수정하는 **Partial Retry**와, 실패를 사전에 방지하는 **Predictive Strategy**까지 수용할 수 있는 아키텍처를 구축해야 합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **Polymorphic State & Strategy**:
    -   `StrategyType`: `CORRECTION`, `RELAXATION`, `REINTERPRETATION`, `DECOMPOSITION` (4대 전략).
    -   **Constraint Management**: `strict_mode`, `retry_depth` 등을 동적으로 조절하는 `ValidationConstraints` 구현.

2.  **Advanced Retry Logic (Logic Resolver)**:
    -   **Pattern Matching**: 에러 로그를 분석하여 최적의 전략을 선택하는 'Meta-Reasoner' 구현.
    -   **Partial Retry Support**: `ValidationFeedback`에 오류가 발생한 `target_fields`를 명시하여, LLM이 해당 필드만 집중적으로 수정하도록 유도.

3.  **Predictive Architecture Ready**:
    -   당장 Classifier를 구현하지 않더라도, State에 `predicted_difficulty`나 `doc_category` 필드를 마련하여 향후 "예측형 라우팅"이 가능하도록 설계.

### Non-Functional Requirements
1.  **Observability**: 현재 어떤 전략(Strategy)이 가동 중인지, 몇 번째 시도(Attempt)인지 명확히 트레이싱 되어야 함.
2.  **Cost Efficiency**: 불필요한 전체 문맥 재생성을 방지하기 위해 Partial Retry 패턴을 적극 활용.

## ✅ Definition of Done
1.  **Framework 구현**: 4가지 전략을 담을 수 있는 State 및 Enum 구현.
2.  **Partial Retry 검증**: Validator가 `target_fields`를 반환하고, Extractor가 이를 인식하여 수정 프롬프트를 생성하는지 확인.
3.  **Strategy Switching**: 에러 상황에 따라 `CORRECTION` -> `RELAXATION` 등으로 전략이 자동 전환되는지 확인.
