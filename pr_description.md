feat(spec-019): advanced chunking strategy implementation

## 📋 Summary
**Spec 019: Advanced Chunking Strategy**를 구현하여 문서 수집 시 RAG 성능 최적화를 위한 의미 단위 분할(Chunking)을 적용했습니다.

기존의 단순 문서 저장 방식(`AtomicDocument` 전체 저장)을 변경하여, 문서를 `CHUNK_SIZE`와 `CHUNK_OVERLAP` 설정에 따라 분할하고 각 청크를 독립적으로 저장하도록 개선했습니다.
- **Before**: 문서를 통째로 저장 및 임베딩.
- **After**: 문서를 청크로 분할하여 Graph DB(Neo4j)와 Vector DB(ChromaDB)에 저장. Neo4j에는 `Document -[:HAS_CHUNK]-> Chunk` 관계가 생성되고, ChromaDB에는 청크 단위 임베딩이 저장됨.

## 🎯 Key Review Points
1. **Chunk Entity & Storage**: `Document`와 `Chunk`의 분리, 그리고 Neo4j에서 관계(`[:HAS_CHUNK]`) 설정 방식이 올바른지 확인해주세요. (`app/infrastructure/storage/neo4j_document_repository.py`)
2. **Chunker Implementation**: LangChain을 활용한 `ChunkerService` 구현 및 설정 적용 여부. (`app/infrastructure/chunker/langchain_chunker.py`)
3. **Ingestion Pipeline**: `IngestionService`가 수집된 문서를 저장하기 전에 Chunking을 수행하고 `save_with_chunks`를 호출하는 흐름. (`app/use_cases/ingestion.py`)

## 🧪 Verification
### Automated Tests
모든 유닛 및 통합 테스트가 통과했습니다.
```bash
uv run pytest tests/unit/test_chunker.py
uv run pytest tests/unit/test_neo4j_storage.py
uv run pytest tests/unit/test_chroma_storage.py
uv run pytest tests/integration/bdd/test_chunking.py -m integration
```

### Manual Verification
Neo4j Graph 확인 시 `(Document)` 노드와 여러 `(Chunk)` 노드가 `HAS_CHUNK` 관계로 연결된 것을 확인했습니다.

## 📦 Files Changed

### 🆕 New Files
- `app/domain/entities/chunk.py`: Chunk Dataclass 정의
- `app/domain/services/chunker.py`: ChunkerService 프로토콜
- `app/infrastructure/chunker/langchain_chunker.py`: LangChain 기반 Chunker 구현
- `tests/unit/test_chroma_storage.py`: ChromaDB Chunk 저장 테스트
- `tests/unit/test_neo4j_storage.py`: Neo4j Chunk 저장 테스트
- `tests/integration/bdd/test_chunking.py`: Chunking 통합 테스트

### 🛠 Modified Files
- `app/core/config.py`: Chunk 설정 추가 (`CHUNK_SIZE`, `CHUNK_OVERLAP`)
- `app/domain/entities/document.py`: `AtomicDocument` -> `Document` 변경. 
    - **Reason**: 문서가 더 이상 Atomic(불가분 최소 단위)하지 않고 Chunk로 분할되는 Container 역할을 하므로, `Document`가 더 적합한 명칭임.
    - `source_url`을 메타데이터로 이동하여 구조 단순화.
- `app/infrastructure/storage/neo4j_document_repository.py`: `save_with_chunks` 구현
- `app/infrastructure/storage/chroma.py`: `save_chunks` 및 `save_with_chunks` 구현
- `app/use_cases/ingestion.py`: Chunking 파이프라인 통합
- `app/interfaces/api/dependencies.py`: Chunker 의존성 주입

## ✅ Definition of Done
- [x] Spec 019: Advanced Chunking Strategy 구현
- [x] LangChain 기반 Recursive Chunking 적용 (Size/Overlap 설정 가능)
- [x] Neo4j에 Chunk 노드 및 관계 저장 구현
- [x] ChromaDB에 Chunk 단위 임베딩 저장 구현
- [x] 모든 관련 Unit/Integration Test 통과
- [x] PR Description 템플릿 준수 및 Walkthrough 작성 완료
