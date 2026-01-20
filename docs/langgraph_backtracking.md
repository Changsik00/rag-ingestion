# LangGraph Backtracking Strategy

LangGraph에서의 백트래킹(Backtracking)은 단순한 재시도가 아니라, **"사고의 전제를 변경하여 문제를 재정의하는 과정"**입니다.
이 문서는 3단계 재시도 레벨과 4가지 핵심 패턴, 그리고 미래의 고급 전략을 정의합니다.

## 1️⃣ Level 1: Execution Retry (기술적 재시도)
> **"같은 생각으로 다시 한 번"**

- **상황**: 일시적 네트워크 오류, API Timeout, JSON 파싱 실패 등.
- **전략**: 질문, 의도, 계획은 변경하지 않고 실행(Execution)만 다시 수행.
- **구현**: `tenacity` 라이브러리나 LangGraph의 기본적인 `recursion_limit` 활용.

## 2️⃣ Level 2: Reasoning Retry (사고 방식 재시도) - **Spec 021 Core**
> **"같은 질문이지만, 사고 방식을 바꿔서"**

- **상황**: 결과가 검증을 통과하지 못함, LLM의 지시 오해.
- **전략**: 질문의 의도는 유지하되, **피드백(Feedback)**을 통해 사고 과정을 교정(Correction).
- **구현**: **Reflexion Pattern** (Validator -> Feedback -> Extractor).

## 3️⃣ Level 3: Question Backtracking (질문 재해석)
> **"우리가 풀려고 한 문제가 애초에 잘못 정의됐을 수 있다"**

- **상황**: 반복된 교정에도 실패, 문서 성격이 초기 가정과 다름.
- **전략**: 문제 정의 자체를 변경 (Re-framing).

---

## 🔁 4 Core Patterns of Question Backtracking

Level 3 백트래킹은 다음 4가지 구체적인 패턴으로 구현됩니다.

### Pattern 1: Ambiguity Backtracking (모호성 되돌리기)
> **"이 질문은 여러 의미로 해석될 수 있다"**
- **상황**: 문서가 여러 스키마로 해석 가능하거나, 현재 스키마가 맞지 않음.
- **전략**: **Schema Switching**. 다른 관점(Schema)으로 다시 추출 시도.
- **예시**: 기술 블로그인 줄 알았으나 채용 공고임 -> `TechSchema` 포기하고 `JobSchema` 적용.

### Pattern 2: Goal Drift Backtracking (목표 재정렬)
> **"사용자의 진짜 목적과 어긋났다"**
- **상황**: 추출은 됐으나 사용자 의도(Use Case)에 부적합함.
- **전략**: **Goal Refinement**. 최종 목표(Goal)를 수정한 뒤 다시 계획 수립.
- **예시**: "요약해줘" (실패) -> "키워드만 뽑아줘" (성공).

### Pattern 3: Constraint Re-evaluation (제약 재설정)
> **"제약이 너무 엄격하다"**
- **상황**: 엄격한 룰(Strict Constraints) 때문에 계속 검증 실패.
- **전략**: **Relaxation**. 제약 조건을 완화(Loosen)하거나 우선순위를 변경.
- **예시**: "인물 5명 필수" (실패) -> "인물 있으면 추출" (성공).

### Pattern 4: Decomposition Backtracking (문제 쪼개기)
> **"질문이 한 번에 풀기에 너무 크다"**
- **상황**: 문서가 너무 길거나 복잡해서 정보 누락 발생.
- **전략**: **Chunking & Aggregation**. 문제를 하위 문제로 쪼개서 해결 후 합침.
- **예시**: 전체 요약 (실패) -> 서론/본론/결론 요약 (성공) -> 통합.

---

## 🔮 Advanced Suggestions: Beyond Reactive Backtracking

사용자의 질문에 대한 AI의 제안: "더 나은 전략은 없는가?"

### 1. Predictive Strategy Selection (예측형 전략)
*현재의 '실패 후 백트래킹(Reactive)' 방식의 단점은 1회 실패 비용이 발생한다는 점입니다.*
- **제안**: **Classifier Node**를 도입하여, 추출 **전에** 문서의 난이도와 타입을 예측하고 최적의 전략을 미리 선택합니다.
- **효과**: 실패 확률을 낮추고, 처음부터 `Chunking`이나 `Relaxed Mode`로 진입하여 비용/시간 절감.

### 2. Partial Retry (부분 백트래킹)
*문서 전체를 다시 읽고 추출하는 것은 비효율적입니다.*
- **제안**: **Field-Level Retry**. 검증에 실패한 특정 필드(Field)만 다시 생성하도록 LLM에 요청.
- **효과**: 이미 잘 추출된 정보(Context)는 유지하고, 오류 부분만 수정하므로 일관성 유지 및 토큰 절약.

### 3. Human-in-the-Loop Checkpointer (협력적 백트래킹)
*AI가 스스로 판단하기 어려운 모호함은 사람에게 물어봐야 합니다.*
- **제안**: `Ambiguity` 점수가 높으면, 임의로 결정하지 말고 **Interrupt**를 걸어 사용자에게 "A입니까 B입니까?" 옵션을 제시.
- **효과**: (Spec 022에서 구현 예정) 치명적 오류 방지.
