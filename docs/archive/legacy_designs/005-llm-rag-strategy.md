# RAG & LLM Strategy: Decision vs. Execution

## 1. 핵심 철학 (Core Philosophy)
> **"LLM은 뇌(Brain), LangGraph는 신경계(Nervous System), 시스템은 기억(Memory/Body)이다."**

우리는 **'LLM의 결정(Decision)'**과 **'시스템의 실행/상태 관리(Execution/State Management)'**를 철저히 분리합니다. LLM이 암묵적인 문맥(Context)에 의존해 상태를 유지하거나 제약 조건을 강제해서는 안 됩니다. LLM은 오직 핵심적인 결정을 내리고, 시스템은 그 결정을 엄격하게 집행해야 합니다.

| 계층 (Layer) | 컴포넌트 (Component) | 역할 (Responsibility) | 예시 (Example) |
|:---:|:---:|:---:|:---|
| **Brain** | LLM (Router) | 의사 결정 (Decision Making) | "문서 A와 B를 비교해줘" -> `{"targets": ["A", "B"]}` 출력 |
| **Nervous System** | LangGraph | 흐름 제어 (Flow Control) | 결정을 검색 노드(Retrieval Node)로 전달 |
| **Memory/Body** | RAG System | 실행 및 강제 (Execution & Enforcement) | `repo.search(filters={"id": ["A", "B"]})` (물리적으로 검색 범위 제한) |

## 2. 피해야 할 안티 패턴 (Anti-Patterns to Avoid)
- **Implicit State (암묵적 상태)**: 명시적인 상태 전달 없이 LLM이 이전 턴의 대화 내용을 "기억하고 있을 것"이라고 기대하는 것.
- **Hallucinated Scope (범위 환각)**: 모든 문서를 다 주면서 LLM에게 프롬프트로만 "관련 없는 문서는 무시해"라고 지시하는 것.
- **System Logic in Prompt (프롬프트 내 로직)**: "사용자가 X라고 하면 Y를 해"와 같은 제어 로직을 그래프 엣지(Edge)가 아닌 프롬프트 텍스트로 처리하는 것.

## 3. 구현 로드맵 (Implementation Roadmap)
1.  **Foundation (Execution Layer)**: 저장소 계층에서 확실한 필터링과 범위 제어 기능 구현 (**Spec 031**).
2.  **Control (Decision Layer)**: *무엇*을 걸러낼지 결정하는 라우터(Router) 및 의도 분류기(Intent Classifier) 구현 (**Spec 032**).
3.  **Orchestration (State Layer)**: LangGraph를 사용하여 '결정'을 '실행'으로 구속력 있게 연결 (**Spec 033**).
