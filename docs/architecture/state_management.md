# State Management Patterns: RAG vs Ingestion

이 문서는 프로젝트 내 두 개의 주요 파이프라인인 **Ingestion Pipeline**과 **RAG Pipeline**이 상태(State)와 히스토리(History)를 다루는 방식의 차이와 그 설계 의도를 설명합니다.

---

## 1. 핵심 요약 (Summary)

| 기능 | Ingestion Pipeline (Agentic) | RAG Pipeline (Retrieval) |
| :--- | :--- | :--- |
| **State Class** | `IngestionGraphState` | `RAGGraphState` |
| **Base Class** | `MessagesState` (LangGraph 기본) | `TypedDict` (LangGraph 기본) |
| **Messages 관리** | `messages` 리스트에 누적 (`add_messages` Reducer) | `history: list[dict]` 필드에 단순 저장 |
| **LLM 활용 방식** | **Reflexion (반성 및 교정)** | **Stateless Generation (일회성 생성)** |
| **설계 철학** | "실수를 기억해야 성장하는 에이전트" | "기억을 최소화하여 정확해진 검색 엔진" |

---

## 2. 상세 분석

### 2.1 Ingestion Pipeline: "스스로 개선하는 Agent"

Ingestion 파이프라인은 불안정한 웹 데이터를 정형화된 메타데이터로 변환하는 작업입니다. 실패할 확률이 높으며, 실패 시 스스로 교정해야 합니다.

*   **상태 관리**: `MessagesState`를 상속받아 사용합니다.
*   **동작 방식**:
    1.  Draft: 초안 생성
    2.  Validate: 검증 실패 (예: "title 필드 누락")
    3.  Feedback: 에러 메시지를 `messages`에 추가 (Reflexion)
    4.  Retry: LLM이 이전 대화(실수+피드백)를 보고 수정된 결과 생성
*   **왜 이렇게 했나?**: LLM은 상태가 없는(Stateless) 함수이므로, 이전의 실수와 피드백을 Context Window(메시지 기록)에 넣어주어야만 "학습 효과"를 낼 수 있습니다.

### 2.2 RAG Pipeline: "정확도 우선 검색 시스템"

RAG 파이프라인은 사용자의 질문에 대해 가장 정확한 답변을 찾아내는 것이 목표입니다.

*   **상태 관리**: `TypedDict`를 사용하며, LangGraph의 `messages` reducer를 사용하지 않습니다.
*   **동작 방식**:
    1.  History: 대화 이력(`history`)은 오직 **Query Rewriter**만 참조합니다.
    2.  Rewrite: Rewriter가 이력을 포함한 질문을 "단일 검색 쿼리"로 압축합니다.
    3.  Generate: Generator는 압축된 쿼리와 검색된 문서(Context)만 보고 답변합니다. 이전 대화 내용은 보지 않습니다.
*   **왜 이렇게 했나?**:
    *   **Hallucination 방지**: 오래된 대화 내용(노이즈)이 검색 결과보다 우선시되는 것을 막습니다.
    *   **일관성**: Generator를 Stateless Search Engine처럼 사용하여, 동일 입력에 대해 (Temperature가 낮을 때) 항상 문서 기반의 근거 있는 답변을 하도록 강제합니다.

---

## 3. Trade-off 및 확장 가이드

### 3.1 언제 이 설계를 바꿔야 하나?

만약 RAG 챗봇을 **"더 대화가 통하는 친구(Chatty Cousin)"**처럼 만들고 싶다면 설계를 변경할 수 있습니다.

*   **변경 방법**: Generator 단계에서 `history`나 `messages`를 프롬프트에 포함시킵니다.
*   **얻는 것**: 사용자의 말투 모방, 농담 받아치기, "아까 했던 말 취소할게" 등의 대화 흐름 포착.
*   **잃는 것 (Risk)**: 검색 정확도 하락. LLM이 문서에 없는 내용을 이전 대화 맥락에서 가져와 답변할 위험(Hallucination)이 증가합니다.

### 3.2 결론

> **RAG는 "기억을 줄여서(Condensed) 정확도를 높인 시스템"이고,**  
> **Ingestion은 "기억을 쌓아서(Reflexion) 완성도를 높이는 시스템"입니다.**

이 아키텍처 결정은 각 파이프라인의 목적(정확한 정보 전달 vs 복잡한 작업 수행)에 최적화된 결과입니다.
