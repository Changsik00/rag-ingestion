# State Management Patterns: RAG vs Ingestion

이 문서는 프로젝트 내 두 개의 주요 파이프라인인 **Ingestion Pipeline**과 **RAG Pipeline**이 상태(State)와 히스토리(History)를 다루는 방식의 차이와 그 설계 의도를 설명합니다.

---

## 1. 한 줄 요약 (Core Concept)

> **"Ingestion은 실수 교정이 중요한 Agent이고, RAG는 현재 질문에 정확히 답하는 검색기입니다."**

| 기능 | Ingestion Pipeline | RAG Pipeline |
| :--- | :--- | :--- |
| **핵심 목적** | 작업 수행 및 오류 수정 (Task Agent) | 정확한 정보 검색 (Search Engine) |
| **State Class** | `IngestionGraphState` (`MessagesState` 상속) | `RAGGraphState` (`TypedDict` 상속) |
| **History 활용** | **적극 활용**: 이전 포맷 에러, 누락된 필드 기억 | **최소화**: 오래된 대화는 노이즈로 취급 |
| **설계 패턴** | Reflexion (반성 및 재시도) | Condensed Retrieval (질문 요약 후 검색) |

---

## 2. 상세 분석: 왜 다르게 설계했을까?

### 2.1 RAG: "정확도 우선(Accuracy First) 검색 시스템"

RAG의 본질은 **"지금 질문에 대해, 가장 관련 있는 문서를 찾아서, 그 범위 안에서만 대답하는 것"**입니다.

#### ❓ 왜 히스토리(Messages)를 버리는가?
`RAGGraphState`는 `messages` 리스트를 State Reducer로 관리하지 않고, 단순히 `history`라는 참고용 필드로만 저장합니다. Generator(답변 생성기)는 이마저도 보지 않습니다. 이유는 다음과 같습니다.

1.  **오래된 대화는 '노이즈'가 된다**:
    *   사용자의 이전 질문, 잡담, 잘못된 가설, 농담 등이 검색 정확도를 오히려 떨어뜨립니다.
    *   Generator가 문서를 보지 않고 이전 대화의 맥락에 끌려가서 그럴듯한 거짓말(Hallucination)을 할 위험이 커집니다.

2.  **Stateless Search Engine 전략**:
    *   **Query Rewriter**가 이미 대화 내역(`history`)을 보고 "완벽한 단일 검색 쿼리"로 요약을 끝냈습니다.
    *   따라서 Generator는 더 이상 복잡한 대화 맥락을 알 필요가 없습니다. 오직 **[압축된 쿼리 + 검색된 문서]**만 보고 깔끔하게 답을 내는 것이 가장 정확합니다.

### 2.2 Ingestion: "스스로 개선하는(Self-Correcting) Agent"

Ingestion 파이프라인은 문서 파싱, 메타데이터 추출, 스키마 검증 등 **실패가 전제된 복잡한 작업**을 수행합니다.

#### ❓ 왜 메시지를 계속 쌓는가?
`IngestionGraphState`는 `MessagesState`를 상속받아 모든 주고받은 메시지를 누적합니다.

1.  **실패 원인을 기억해야 한다**:
    *   `Extract` -> `Validate` -> `Fail` 상황에서, "아, 지난번에 'title' 필드가 없다고 에러가 났었지?"를 기억해야 합니다.
    *   이 기억이 없으면 에이전트는 똑같은 실수를 무한히 반복합니다.

2.  **Reflexion (반성 모드)**:
    *   LLM은 상태가 없는 함수입니다. 따라서 `messages` 리스트 자체가 LLM의 **"작업 기억 + 반성 노트"** 역할을 합니다.
    *   시스템이 주는 에러 메시지(Feedback)와 자신의 이전 시도(Attempt)를 모두 입력으로 넣어주어야만, 다음 시도에서 더 나은 결과를 낼 수 있습니다.

---

## 3. 이 설계의 장단점 (Trade-off)

### ✅ RAG 파이프라인 설계
*   **장점**: Hallucination 감소, 항상 문서 근거 기반 답변, 토큰 비용 절약, 디버깅 용이(입력이 단순함).
*   **단점**: "스타일"이나 "톤"을 유지하기 어려움. ChatGPT처럼 "아까 했던 농담"을 기억해서 받아치는 인간적인 대화 능력은 부족함.

### ✅ Ingestion 파이프라인 설계
*   **장점**: 반복적인 에러를 스스로 수정 가능, 복잡한 비정형 데이터 처리에 강력함.
*   **단점**: 메시지가 쌓일수록 토큰 비용 증가, 무한 루프 위험(따라서 최대 재시도 횟수 제한 필수).

---

## 4. 결론 (Architectural Decision)

이 프로젝트는 **각 파이프라인의 목적에 맞춰 상태 관리 전략을 이원화**했습니다.

> **RAG는 "기억을 줄여서(Condensed) 정확도를 높인 시스템"이고,**  
> **Ingestion은 "기억을 쌓아서(Reflexion) 완성도를 높이는 시스템"입니다.**

만약 RAG를 더 "수다스러운 친구"처럼 만들고 싶다면 Generator에 `history`를 주입하도록 변경할 수 있지만, 이는 검색 정확도와의 Trade-off가 있음을 명심해야 합니다.
