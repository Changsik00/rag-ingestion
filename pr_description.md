feat(spec-019): Advanced Chunking Strategy Implementation

## 📝 Description
**Spec 019: Advanced Chunking Strategy**를 구현하여 문서 수집 시 RAG 성능 최적화를 위한 의미 단위 분할(Chunking)을 적용했습니다.

기존의 단순 문서 저장 방식에서 벗어나, 문서를 설정된 크기(`CHUNK_SIZE`)와 중복(`CHUNK_OVERLAP`)을 가진 청크(Chunk)로 분할하여 저장합니다. 이를 통해 Vector DB(ChromaDB)에서는 더 정교한 임베딩 검색이 가능해지며, Graph DB(Neo4j)에서는 문서와 청크 간의 구조적 관계를 보존합니다.

## 🎯 Key Changes

### 1. Configuration & Setup
- `app/core/config.py`: `CHUNK_SIZE` (1000), `CHUNK_OVERLAP` (200), `GEMINI_API_KEY` 등 환경 설정 중앙화 (Pydantic BaseSettings).

### 2. Domain Layer
- `Chunk` Entity 추가: `id`, `content`, `parent_id`, `index`, `metadata`.
- `ChunkerService` Protocol 정의.
- `Document` Entity 리팩토링: `AtomicDocument` -> `Document`, `source_url`을 메타데이터로 이동.

### 3. Infrastructure Layer
- **Chunker**: `LangChainChunker` 구현 (LangChain `RecursiveCharacterTextSplitter` 활용).
- **Neo4j Storage**: `save_with_chunks` 메서드 구현 (`Document` -[:HAS_CHUNK]-> `Chunk` 관계 저장).
- **Chroma Storage**: `save_chunks` 구현 (Chunk 단위 임베딩 저장).
- **Composite Storage**: 두 저장소 간 저장 로직 조율.

### 4. Application Layer
- `IngestionService`: `ChunkerService` 주입 및 수집 파이프라인 내 Chunking 단계 추가.

## ✅ Verification
- **Unit Tests**:
    - `test_chunker.py`: 분할 로직 및 메타데이터 검증.
    - `test_neo4j_storage.py`: Chunk 노드 생성 Query 검증.
    - `test_chroma_storage.py`: Chunk 임베딩 저장 로직 검증.
    - `test_ingestion_service.py`: 서비스 파이프라인 통합 검증.
- **Integration Tests**:
    - `tests/integration/bdd/test_chunking.py`: 실제 API 요청 시 Chunk 저장 흐름(Spy) 검증.

## 📸 Screenshots / Diagrams
(Neo4j Graph Structure Concept)
`(Document) --[:HAS_CHUNK]--> (Chunk 1)`
`(Document) --[:HAS_CHUNK]--> (Chunk 2)`

## 🔗 Related Issues
- Resolves Spec 019
- Updates Spec 018 (Completed)
