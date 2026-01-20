# Spec 023 Design Guide: Reasoning Context & Failure Analysis

> **User Feedback Summary**: "State is currently just a 'Status', not a 'Continuity of Thought'."

이 문서는 Spec 023 구현을 위한 핵심 설계 가이드라인입니다. 사용자가 제공한 "사고의 흐름으로 디버깅하기" 위한 아키텍처 피드백을 원문 그대로 보존하고, 이를 기술 요구사항으로 번역합니다.

---

## 🛑 The Core Problem
**"이 에이전트는 retry는 하지만 ‘왜 retry 하는지에 대한 기억(사고 맥락)’이 없다."**

- **Feedback**: 결과(`message`)는 있지만 원인(`cause`)이 없다.
- **Strategy**: 행동(`CORRECTION`)은 바뀌지만 전제(`Assumption`)는 그대로다.
- **History**: 단순 로그(`steps_history`)이지 기억(`Context`)이 아니다.

---

## 🏗️ Required Data Structures (State)

### 1. Failure Hypothesis (실패 가설)
> "우리는 왜 실패했는가?"

```python
class FailureHypothesis(TypedDict):
    cause: str                 # e.g., "missing_info", "ambiguous_schema", "strict_constraints"
    description: str           # Human-readable explanation
    invalid_assumptions: list[str]  # e.g., ["The document has explicit titles"]
```

### 2. Interpretation History (질문 해석 이력)
> "이 질문을 우리는 어떻게 해석해왔는가?"

```python
class QuestionInterpretation(TypedDict):
    version: int
    interpretation: str  # e.g., "Extract as a Technical Blog Post"
    reason_for_change: str # e.g., "Detected job posting keywords"
```

### 3. Decision Trace (의사결정 추적)
> "왜 이 전략을 선택했는가?"

```python
class DecisionTrace(TypedDict):
    retry_count: int
    selected_strategy: StrategyType
    reason: str  # e.g., "Repeated validation failure on 'summary' field"
```

---

## 🔄 Revised Graph Flow

실패 분석과 전략 결정을 분리해야 합니다.

**Existing**:
`extract` → `validate` → `resolve` (Mix of analysis & strategy) → `extract`

**Proposed**:
1.  **Extract**: (Prompt includes `Interpretation`)
2.  **Validate**: (Fails)
3.  **Analyze Failure** (New Node): 
    - Rule/LLM based classification
    - Generates `FailureHypothesis`
4.  **Reinterpret Question** (New Node):
    - Uses `FailureHypothesis` to update `Assumption`
    - Generates new `QuestionInterpretation`
5.  **Resolve Strategy**:
    - Selects `StrategyType` based on analysis
6.  **Extract**: (Retry with NEW mental model)

---

## 📝 Prompt Engineering (The "Why")

**Prompt가 변경되어야 하는 방향**:

❌ **AS-IS (Result Only)**:
```
Previous attempt failed.
Error Message: Title is missing.
```

✅ **TO-BE (Reasoning Context)**:
```
You are retrying because the previous extraction failed due to:
- Cause: Missing required entity fields (FailureHypothesis)
- Incorrect assumption: The document explicitly lists entities

Re-interpret the content assuming:
- Some entities may be implicit (New Interpretation)
- Approximation is acceptable
```

---

## ✅ Implementation Checklist

1.  [ ] **State Upgrade**: `backtracking_context` 필드 추가 (Hypothesis, Interpretation, Trace).
2.  [ ] **Failure Analyzer Node**: `ValidationFeedback`을 `FailureHypothesis`로 변환하는 로직.
3.  [ ] **Interpreter Node**: 실패 원인을 바탕으로 "질문 재정의(Re-framing)" 수행.
4.  [ ] **Prompt Injection**: `construct_extraction_prompt`에 "Why" 섹션 추가.
