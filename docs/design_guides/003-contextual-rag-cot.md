# Design Guide 003: Contextual RAG & CoT Prompting

## 1. 개요 (Overview)
**Contextual RAG**는 사용자의 다중 턴(Multi-turn) 대화를 단일 턴(Single-turn) 검색 쿼리로 변환하여, 검색 엔진이 문맥을 이해할 수 있게 하는 기술입니다.
본 가이드는 초기 구현 시 발생했던 **문맥 소실(Context Drift)** 문제와 이를 **CoT(Chain of Thought) 프롬프팅**으로 해결한 경험을 기록합니다.

## 2. 문제 상황: 문맥 소실 (Context Drift) - "Recency Bias"

RAG 대화가 길어질 때, LLM이 가장 최근의 대화 주제에만 집중하여 과거의 핵심 엔티티를 잊어버리는 현상이 발생했습니다.

### 실패 시나리오 (Before)
1.  **Q1**: "일론 머스크의 고등학교는?" -> A: "프리토리아 남학교" (Context: **Elon Musk**)
2.  **Q2**: "그가 만든 **자동차**는?" -> A: "테슬라" (Context: **Car**)
3.  **Q3**: "그 학교는?" -> **Rewritten**: "자동차 학교는?" or "그 학교는 어디인가?" (Fail)
    *   **원인**: LLM이 직전 턴의 '자동차'에 휩쓸려(Recency Bias), '그(He)'가 '일론 머스크'임을 놓침.

## 3. 해결책: CoT 기반 프롬프팅 (Solution)

단순히 "질문을 고쳐줘"라고 하는 대신, **사고의 단계(Analysis Steps)**를 명시하여 LLM이 강제로 전체 문맥을 훑어보게 만들었습니다.

### 핵심 코드 (`app/domain/services/query_rewriter.py`)

```python
prompt = f"""
You are an expert search query refiner.
...
**Analysis Steps:**
1. Read the "Chat History" to understand the current topic, key entities (people, companies, technologies), and context.
2. Analyze the "Follow Up Input". Identify pronouns (he, she, it, they) or implicit references.
3. REPLACE ambiguous references with specific terms from the history.
4. APPEND missing context if the input is too short.
...
"""
```

*   **Step 1**: "주제(Topic)와 핵심 엔티티(Key Entity)를 먼저 파악하라"고 지시 -> **Recency Bias 극복**.
*   **Step 3**: 모호한 지칭(He, That)을 구체적 용어(Elon Musk)로 치환하라.

### 개선 결과 (After)
*   **Q3**: "그 학교는?" -> **Rewritten**: "**일론 머스크가 다닌 프리토리아 남학교는** 어떤 학교야?" (Success)
*   중간에 다른 주제(자동차)가 섞여도 핵심 인물을 정확히 회상(Recall)함.

## 4. 검증 (Verification)

`tests/integration/test_query_rewrite_flow.py`의 `test_rewriter_value_add_verification`를 통해 Rewriter의 효용성을 증명했습니다.

| 구분 | Raw LLM (No Rewriter) | Contextual Rewriter Service |
| :--- | :--- | :--- |
| **Input** | "Where is his school?" | "Where is his school?" (+ History) |
| **Output** | "Where is his school?" (누구?) | "**Where did Elon Musk go to school?**" |
| **결과** | **검색 불가** (문맥 소실) | **검색 성공** (문맥 유지) |

## 5. 결론 (Takeaway)
RAG에서 검색 품질은 **"질문을 얼마나 잘 다듬느냐"**에 달려 있습니다.
단순한 히스토리 주입을 넘어, **CoT(연쇄 추론) 기법**을 프롬프트에 적용함으로써 **대화의 안정성(Stability)**을 획기적으로 높일 수 있습니다.
