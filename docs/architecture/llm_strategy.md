# LLM & RAG Strategy Guide

이 문서는 프로젝트에서 사용하는 LLM, 임베딩, 그리고 텍스트 분할(Chunking) 전략을 기술합니다.

## 1. Embedding Strategy

### 1.1 기술 스택
- **Model**: Google Gemini Embedding (`models/embedding-001` or equivalent)
- **Library**: `langchain-google-genai`
- **Vector DB**: ChromaDB

### 1.2 선정 이유
- **성능**: Google의 멀티모달 이해 능력을 바탕으로 한 고품질 벡터 생성.
- **통합성**: Gemini LLM과 같은 생태계를 사용하여 관리가 용이함.
- **비용 효율성**: 타사 엔터프라이즈 임베딩 대비 경쟁력 있는 가격 및 속도.

---

## 2. Chunking Strategy

RAG(Retrieval-Augmented Generation)의 성능은 "얼마나 적절한 문맥을 찾아내는가"에 달려 있으며, 이를 결정하는 핵심 요소가 청킹(Chunking)입니다.

### 2.1 Current Strategy: Recursive Character Chunking (with Overlap)

Phase 4 (Spec 019)에서 채택한 표준 전략입니다.

- **Method**: `RecursiveCharacterTextSplitter` (LangChain)
- **Logic**:
    1. 문단(`\n\n`), 줄바꿈(`\n`), 공백(` `) 순으로 구분자를 찾아 텍스트를 나눕니다.
    2. 설정된 `CHUNK_SIZE`(예: 1000자)를 넘지 않도록 자릅니다.
    3. **Context Overlap**: 청크와 청크 사이를 `CHUNK_OVERLAP`(예: 200자)만큼 겹치게 하여 문맥 단절을 방지합니다.
- **장점**:
    - **Speed**: 별도의 모델 추론 없이 텍스트 처리만 하므로 매우 빠릅니다.
    - **Cost**: API 호출 비용이 0원입니다 (Open Source Logic).
    - **Efficiency**: 대부분의 일반적인 문서에서 준수한 성능을 보장합니다.

### 2.2 Future Alternative: Google Semantic Chunking

검색 정확도를 극한으로 끌어올려야 할 때 고려할 수 있는 차세대 전략입니다. (Backlog 등록됨)

- **Method**: Google AI 기반 Semantic Chunking
- **Logic**: AI 모델이 텍스트의 의미를 해석하여 "주제가 바뀌는 지점"을 찾아 분할합니다.
- **Trade-off**:
    - **Pros**: 사람이 문서를 읽고 정리한 것처럼 자연스러운 단위로 나뉩니다.
    - **Cons**: 모든 텍스트를 AI 모델에 통과시켜야 하므로 **비용과 시간(Latency)**이 증가합니다.

---

## 3. Storage Structure

- **Graph Structure (Neo4j)**:
  `(:Document)-[:HAS_CHUNK]->(:Chunk)`
  원본 문서와 그 파편들을 구조적으로 연결하여 관리합니다.

- **Vector Index (ChromaDB)**:
  임베딩은 `Document` 레벨이 아닌 `Chunk` 레벨에서 수행합니다. 이를 통해 질문과 가장 유사한 "구체적인 문단"을 정밀하게 검색할 수 있습니다.
