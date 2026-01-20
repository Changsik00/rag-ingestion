# Spec-023: Reasoning Context & Failure Analysis

## 📋 배경 및 문제 정의 (Background & Problem)
현재 1차적 Backtracking(Spec 021)은 단순한 상태(`retry_count`)와 결과(`error`)에 기반하여 재시도를 수행합니다.
하지만 에이전트는 "왜 실패했는지"에 대한 **사고의 맥락(Reasoning Context)**이 부재하여, 전략(`CORRECTION`, `RELAXATION`)은 변경되지만 근본적인 전제(`Assumption`)는 수정되지 않는 문제가 있습니다.

1. **No Logic Continuity**: 재시도 시 이전 실패의 원인 분석 없이 단순히 "다시 해"라고 지시합니다.
2. **Static Assumption**: "문서에 제목이 반드시 있다"와 같은 암묵적 전제가 실패 상황에서도 유지됩니다.
3. **Result-Oriented**: 로그에는 결과만 남고, 왜 그런 전략을 선택했는지에 대한 의사결정 과정(Trace)이 남지 않습니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. `IngestionState`에 `backtracking_context` 필드를 추가하고, `FailureHypothesis`, `InterpretationHistory`, `DecisionTrace` 구조체를 정의해야 합니다.
2. 검증 실패 시 이를 분석하는 `analyze_failure` 노드를 구현해야 합니다. (Rule-based 우선)
3. `construct_extraction_prompt` 함수는 `FailureHypothesis`와 `QuestionInterpretation`을 반영하여 "Why" 섹션을 포함해야 합니다.

### Non-Functional Requirements
1. **Traceability**: 모든 의사결정(전략 변경, 가설 수립)은 로그 또는 상태에 명시적으로 남아야 합니다.
2. **Maintainability**: 분석 로직은 Rule 기반으로 시작하되, 추후 LLM 기반으로 확장 가능하도록 구조화해야 합니다.

## ✅ Definition of Done
1. `IngestionState`에 Reasoning Context 관련 필드가 정의됨.
2. 실패 시 `analyze_failure`가 실행되고, `FailureHypothesis`가 생성되는지 테스트로 검증됨.
3. 재시도 프롬프트에 실패 원인과 새로운 가설이 포함되는지 확인됨.
4. Test Coverage 유지 및 Integration Test 통과.
