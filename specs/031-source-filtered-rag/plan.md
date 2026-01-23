# Implementation Plan: Spec-031 Source-Filtered RAG

## 📋 Branch Strategy
- `feature/spec-031-source-filtered-rag`

## 🛑 User Review Required
> [!IMPORTANT]
> **Interface Change**: `DocumentRepository.search(query, ...)` 메소드 시그니처가 변경되어 `filters: dict | None`을 받게 됩니다.
> **Scope**: 이 스펙은 "문서 단위"의 물리적 필터링을 구현합니다. 이는 향후 **Router LLM(Spec 032)**이 내릴 결정을 집행하는 "손과 발"이 됩니다.

## 🎯 Core Strategy
**"System Enforces Scope"**: 사용자가 선택한(또는 Router가 결정한) 문서 범위를 저장소 계층에서 물리적으로 차단합니다.
프롬프트 엔지니어링에 의존하는 것이 아니라, DB 쿼리 레벨(`WHERE`, `$in`)에서 원천 봉쇄하여 **Context Pollution**을 0%로 만듭니다.

### 데이터 흐름
`Admin UI (Multiselect)` -> `RAGService (filters={"doc_id": ["A", "B"]})` -> `CompositeStorage` -> `Neo4j (IN Query)` / `Chroma ($in match)`

## 📂 Proposed Changes

### 1. Domain Layer (인터페이스 정의)

#### [MODIFY] [document_repository.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/interfaces/document_repository.py)
- `search` 메소드 시그니처 수정: `filters: dict | None = None` 추가.
- `key: value` (Single) 및 `key: [value1, ...]` (List) 지원 명시.

### 2. Infrastructure Layer (저장소 구현)

#### [MODIFY] [neo4j_document_repository.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/neo4j_document_repository.py)
- **Cypher Query Builder**:
    - `filters` 딕셔너리를 파싱하여 `WHERE` 절 동적 생성.
    - List Value 감지 시 `IN` 연산자 사용 (`d.doc_id IN $ids`).
    - Single Value 감지 시 `=` 연산자 사용.

#### [MODIFY] [chroma.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/chroma.py)
- **Metadata Filter Adapter**:
    - List Value 감지 시 Chroma 문법 `{"key": {"$in": [...]}}`로 변환.
    - Single Value는 그대로 전달.

#### [MODIFY] [composite.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/composite.py)
- 필터 인자를 하위 저장소로 투명하게 전달(Pass-through).

### 3. Application Layer (비즈니스 로직)

#### [MODIFY] [rag_service.py](file:///Users/ck/Project/doit/rag-ingestion/app/use_cases/rag_service.py)
- `retrieve_and_generate`: `filters` 인자를 받아 `contextual_rag` 및 `search` 로직에 전파.
- **Context Handling**: 필터가 적용된 경우, 검색 결과가 물리적으로 제한되므로 LLM은 자연스럽게 해당 컨텍스트 내에서만 답변생성.

### 4. Admin UI (사용자 경험)

#### [MODIFY] [4_RAG_Playground.py](file:///Users/ck/Project/doit/rag-ingestion/app/admin/pages/4_RAG_Playground.py)
- **Knowledge Source**: `st.multiselect` 도입.
- 빈 값일 경우: 전체 검색 (기존 동작).
- 값 선택 시: 선택된 문서 ID 리스트를 필터로 전달.

## 🧪 Verification Plan

### Automated Tests
*새로운 통합 테스트 파일 생성*: `tests/integration/test_filtered_search.py`

#### Scenario 1: The "Homonym" Test (Isolation)
- **Setup**: `Source A`(Apple Tech), `Source B`(Apple Fruit).
- **Action**: `Source A` 필터 적용 후 "애플의 특징?" 질문.
- **Check**: 답변에 '과일', '식물' 관련 단어가 **전혀** 없어야 함.

#### Scenario 2: The "Context Switch" Test (System Priority)
- **Setup**: `Source A`(Tech) 필터.
- **Action 1**: "스티브 잡스가 누구야?" -> 답변 생성 (Tech Context 형성).
- **Action 2**: 필터를 `Source B`(Fruit)로 **변경**.
- **Action 3**: "애플의 신제품은?" (문맥상 아이폰을 묻는 듯한 질문).
- **Check**: 시스템이 Tech 문서를 차단했으므로, LLM은 '신제품'을 찾지 못하거나 '과일' 관점에서 답변해야 함. (Tech 답변 나오면 Fail)

#### Scenario 3: The "Source Injection & Purity" Test
- **Setup**: `Source A` 대화 진행 중.
- **Action 1**: 새로운 URL `Source C` (예: 기계식 키보드) Ingest 및 필터 선택.
- **Action 2**: "이 내용 정리해줘".
- **Check**: 이전 대화(A)의 잔상 없이, 오직 `Source C`의 내용만 요약되어야 함.
