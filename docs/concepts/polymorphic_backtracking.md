# Polymorphic Backtracking Strategy (The 4 Strategies)

사용자님의 제안대로 **4가지 전략을 모두 수용하는 아키텍처**를 설계합니다.
핵심은 `Logic Resolver`가 단순히 "재시도 할까?"를 결정하는 것이 아니라, **"어떤 전략으로 재시도 할까?"**를 결정하는 **Meta-Reasoner**가 되는 것입니다.

## 🏗️ Architecture: The Strategy Selector

검증 실패 시, `Logic Resolver`는 실패 원인(`Feedback`)을 분석하여 다음 4가지 전략 중 하나를 선택합니다.

### 1️⃣ Reasoning Retry (Correction)
- **상황**: LLM이 지시를 단순 오해했거나, 사소한 실수를 함.
- **Action**: "이전 에러가 이러했으니 고쳐라" (Reflexion).
- **Update**: `strategy="CORRECTION"`, `prompt` += `feedback`.

### 2️⃣ Ambiguity Backtracking (Re-interpretation)
- **상황**: 문서가 모호하여 엉뚱한 스키마로 추출됨. (예: 기술 블로그인 줄 알았는데 채용 공고임)
- **Action**: "이 문서는 B 타입 같다. B 스키마로 다시 추출하자."
- **Update**: `target_schema="JOB_POSTING"`.

### 3️⃣ Constraint Re-evaluation (Relaxation)
- **상황**: 품질 기준이 너무 높아 반복적으로 실패함. (예: 요약문 3줄 요구했으나 계속 5줄 나옴)
- **Action**: "3줄 제약을 완화하여 5줄도 허용하자."
- **Update**: `validation_rules.strict_mode = False`.

### 4️⃣ Decomposition Backtracking (Chunking)
- **상황**: 문서가 너무 길거나 복잡해서 추출이 누락됨.
- **Action**: "한 번에 안 되니 쪼개서 처리하자."
- **Update**: `processing_mode="CHUNKED"`.

---

## 🚀 Implementation Strategy for Spec 021

한 번에 4가지를 모두 "완벽하게" 구현하려면 로직이 너무 비대해질 수 있습니다.
따라서, **Spec 021에서는 이 4가지를 담을 수 있는 "그릇(Framework)"을 완벽하게 만드는 것**을 목표로 합니다.

1.  **State 설계**: 4가지 전략을 모두 표현할 수 있는 유연한 State (`current_strategy`, `active_constraints`, `schema_type`).
2.  **Logic Resolver**: 에러 타입에 따라 전략을 매핑하는 `Strategy Selector` 구현.
3.  **Prioritization**:
    -   1순위: **Reasoning Retry** (기본)
    -   2순위: **Constraint Relaxation** (임계값 조정)
    -   (Ambiguity와 Decomposition은 Mocking으로 흐름만 검증하거나, 간단한 규칙만 적용)

이 접근 방식(Framework First)이 4가지 전략을 모두 시도해보고 싶다는 요구사항을 가장 안정적으로 충족시킬 것입니다.
