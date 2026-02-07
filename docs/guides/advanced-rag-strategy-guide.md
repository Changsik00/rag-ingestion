# Advanced RAG Optimization & Hybrid Retrieval Strategy

이 문서는 사용자의 질문 의도를 정확히 파악하고, 유실 없는 지식 추출 및 연결을 통해 최상의 답변을 도출하기 위한 **고급 RAG(Retrieval-Augmented Generation) 기법**들을 정리합니다.

---

## 1. 핵심 적용 테크닉 (Implemented Techniques)

### 🧩 GraphRAG: 지식 그래프 증강 검색
단순히 텍스트의 유사성(Vector)만 보는 것이 아니라, 데이터 간의 명시적인 **관계(Relationship)**를 추적합니다.
- **Star-Schema Heuristic (성형 구조 가드레일)**: 특정 프로그램(예: 어쩌다 어른)의 정보임을 인지하면, 추출된 모든 엔티티를 해당 프로그램 노드에 자동으로 연결하여 지식의 밀도를 높입니다.
- **Path Traversal**: "A와 B의 관계가 뭐야?"라는 질문에 대해 벡터 검색보다 훨씬 정확한 인과관계를 제공합니다.

### 🏷️ Context-Aware Ingestion (맥락 보존형 수집)
AI가 수집 단계에서 데이터의 출처(Source)를 잊어버리지 않도록 하는 기법입니다.
- **Metadata Injection**: 추출 단계에서 AI에게 "이 텍스트는 [어쩌다 어른] 프로그램의 대본임"이라는 메타데이터를 주입합니다.
- **Enforced Extraction**: 요약문이나 키워드에 반드시 출처 정보를 포함하도록 프롬프트를 강화하여, 나중에 '프로그램명'으로 검색했을 때 검색 결과에서 누락되는 현상을 방지합니다.

### 🔄 Intelligent Query Rewriting (의도 기반 검색 쿼리 재작성)
대화 이력을 분석하여 사용자의 모호한 질문을 검색 최적화된 독립적 질문(Standalone Query)으로 변환합니다.
- **Redundancy Preservation**: "어쩌다 어른"처럼 반복되는 고유 명사를 AI가 생략하지 않고 검색의 핵심 키워드로 유지하도록 튜닝했습니다.
- **Entity Identification**: 질문 속에서 숨겨진 엔티티를 찾아 검색 필터로 변환합니다.

### ⚖️ Hybrid Search & LLM Reranking (하이브리드 검색 및 재순위화)
- **Multi-Vector Retrieval**: Vector(의미), Keyword(형태), Graph(관계) 결과를 모두 가져옵니다.
- **Pointwise/Listwise Reranking**: 검색된 수십 개의 조각 중, 실제 질문과 가장 일맥상통하는 상위 3-5개만 골라냅니다. 이때 AI에게 "맥락이 맞지 않으면 과감히 0점을 주라"고 지시하여 정확도를 높입니다.

### 🔗 Entity Normalization & Alias Management (엔티티 정규화 및 별칭 관리)
한국어의 특징인 띄어쓰기 변동성과 다양한 줄임말을 처리하여 지식 그래프의 파편화를 방지합니다.

#### 🧠 무엇이 달라졌나요? (Optimization Logic)
- **소스 메타데이터 주입 (Source Context)**: 이전에는 AI가 영상의 '텍스트(자막)'만 봤다면, 이제는 영상의 제목과 채널명(예: 세바시 강연) 정보를 분석 단계에서 함께 전달받습니다.
- **추론 엔진 강화 (Reasoning Engine)**: LLM에게 "자막에 '세바시'라고 적혀있더라도, 채널명이나 제목에 브랜드 정보가 있다면 이를 **세상을 바꾸는 시간 15분** 같은 정식 명칭(Canonical Name)으로 스스로 추론하여 연결하라"는 명시적인 추론 지침을 추가했습니다.
- **동적 별칭 도출**: 이제 AI는 고정된 리스트가 아니라, 메타데이터 사이의 관계를 분석하여 "세바시 강연" 채널의 영상이니 "세바시"는 이 프로그램의 별칭이라는 것을 스스로 이해하고 지식 그래프에 `ALIAS_OF` 관계로 기록합니다.

#### ⚙️ 코드 변경 증거 (Technical Implementation)
1. **AI에게 '눈'을 달아줌 ([langchain_extractor.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/ai/langchain_extractor.py))**
   - `PromptTemplate`에 `{metadata}` 변수를 추가하여 AI가 영상 제목과 채널명을 볼 수 있게 했습니다.
   - `aextract_metadata(..., metadata=metadata)` 처럼 딕셔너리를 받아 JSON 문자열로 변환해 AI에게 넘기는 로직을 구현했습니다. (확인: [L110: SOURCE METADATA: {metadata}](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/ai/langchain_extractor.py#L110))
2. **지능형 추론 지침 주입 (Prompt Logic)**
   - 프롬프트 내부에 "약어(세바시)를 보면 정식 명칭(세상을 바꾸는 시간 15분)으로 복원하라"는 **Deep Semantic Alignment** 규칙을 코드로 심었습니다. (확인: [L84: Canonical Naming & Abbreviation Resolution](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/ai/langchain_extractor.py#L84))
3. **지능형 그래프 연결 ([ingestion.py](file:///Users/ck/Project/doit/rag-ingestion/app/application/services/ingestion.py))**
   - `_build_knowledge_graph` 함수에서 `normalize_entity_name` 유틸리티를 호출하여 띄어쓰기를 제거한 ID로 노드를 병합합니다.
   - AI가 찾아낸 별칭들을 `ALIAS_OF`라는 실제 그래프 관계로 생성하는 루프를 추가했습니다. (확인: [L281: normalized_name = normalize_entity_name(name)](file:///Users/ck/Project/doit/rag-ingestion/app/application/services/ingestion.py#L281))

---

## 2. AI(LLM) 의존의 한계와 최적화 기법

AI는 강력하지만 **비결정적(Non-deterministic)**입니다. 즉, 똑같은 입력에도 가끔 다른 결과를 내거나 핵심 맥락을 놓칠 수 있습니다. 이를 보완하기 위한 최적의 전략은 다음과 같습니다.

### 🛠️ 기법 1: Deterministic Guardrails (결정적 가드레일)
- **언제 사용하나?**: 절대로 놓치면 안 되는 핵심 관계(예: 프로그램명, 작성자)를 연결할 때.
- **방법**: AI의 추론에만 맡기지 말고, 코드 레벨에서 메타데이터를 기반으로 관계를 **강제 형성(Heuristic Rules)**하십시오. 이번에 적용된 `Star-Schema`가 대표적인 예입니다.

### 🧠 기법 2: Prompt-Driven Extraction vs Structured Reasoning
- **언제 사용하나?**: 방대한 양의 텍스트에서 의미를 추출할 때.
- **방법**: AI에게 단순히 "요약해줘"라고 하지 말고, **추출 형식을 강제(Pydantic Schema)**하고 **실패 시 이유를 분석(Backtracking)**하도록 설계하십시오.

### 🔍 기법 3: Hybrid Search (Intelligence + Exact Match)
- **최선의 결과 도출법**: 
    - **Vector Search**: "비슷한 느낌"의 문장을 찾는 데 사용
    - **Keyword Search**: "정확한 단어(어쩌다 어른)"를 찾는 데 사용
    - **Graph Search**: "관계와 맥락"을 파악하는 데 사용
    - 이 세 가지 결과를 **Reranker(심판)**에게 맡기는 구조가 현재 수준에서 가장 완벽한 RAG 결과를 만듭니다.

---

## 3. 요약: 최상의 결과를 위한 Golden Rules

1.  **Metadata is King**: 데이터의 본문만큼이나 '출처'와 '카테고리'가 중요합니다. 이를 수집 단계에서 잃어버리면 복구가 불가능합니다.
2.  **Structural Integrity**: 그래프 DB를 활용해 엔티티 간의 선을 미리 그어두십시오. 검색 성능이 기하급수적으로 향상됩니다.
3.  **Iterative Refinement**: Reranker의 점수 부여 로직을 상시 모니터링하고, 특정 상황(예: 인물 혼동)에 대한 페널티 지침을 지속적으로 업데이트하십시오.

> [!TIP]
> 이번 "어쩌다 어른" 사례처럼 특정 키워드 검색이 안 될 때는 **수집 단계의 메타데이터 보존율**을 가장 먼저 점검해야 합니다.
