# Plan 002: Atomic Storage & Swagger Admin Implementation

## 1. Goal Description
수집된 데이터를 단순히 마크다운으로 반환하는 것을 넘어, **Neo4j**와 **ChromaDB**에 실제로 영구 저장하는 기능을 구현합니다.
- **Neo4j**: 문서의 메타데이터와 구조적 관계(Document -[HAS_PART]-> Chunk) 저장.
- **ChromaDB**: 문서의 텍스트 임베딩 저장 (Semantic Search 용).
- **Swagger Admin**: 저장된 문서를 API를 통해 조회하여 검증 가능하게 함.

## 2. Proposed Changes

### Configuration
#### [NEW] `docker-compose.yml`
- Neo4j 5.x (with APOC)
- ChromaDB Latest

#### [MODIFY] `pyproject.toml`
- Add `neo4j`, `chromadb` clients.

### Domain Layer
#### [NEW] `app/domain/entities/document.py`
- `AtomicDocument`: DB에 저장될 핵심 엔티티 (Life-cycle 있음).

#### [NEW] `app/domain/value_objects/source.py`
- `Source`: URL 및 메타데이터를 포함하는 값 객체 (Immutable).

#### [NEW] `app/domain/interfaces/document_repository.py`
- `DocumentRepository`: 저장소에 대한 추상 인터페이스 (Repository Pattern).

### Infrastructure Layer (Storage)
#### [NEW] `app/infrastructure/storage/neo4j.py`
- Neo4j 연결 및 Cypher 쿼리 실행.

#### [NEW] `app/infrastructure/storage/chroma.py`
- ChromaDB 컬렉션 관리 및 임베딩 저장.

#### [NEW] `app/infrastructure/storage/composite.py`
- 두 DB에 트랜잭션(논리적) 단위로 저장을 수행하는 Facade.

### Infrastructure Layer (Adapters)
#### [NEW] `app/infrastructure/adapters/http_client.py`
- 외부 요청을 위한 공통 HTTP 클라이언트 (Wrapper).

### Application Layer
#### [MODIFY] `app/use_cases/ingestion.py`
- `BasicWebScraper`가 반환한 `IngestResponse`를 `AtomicDocument`로 변환하여 `StorageInterface.save()` 호출.

### Interface Layer
#### [MODIFY] `app/interfaces/api/main.py`
- `POST /ingest/web` 업데이트 (저장 플래그 추가).
- `GET /documents` 추가 (저장된 문서 확인용).

## 3. Verification Plan

### Automated Tests
- **Integration Test**: 로컬 Docker에 떠있는 DB에 실제 연결하여 저장/조회 테스트.
- **Unit Test**: `StorageInterface` Mocking을 통해 Service 로직 검증.

### Manual Verification
1. `docker-compose up -d`로 DB 구동.
2. `POST /ingest/web`으로 URL 전송.
3. Neo4j Browser(`http://localhost:7474`)에서 `MATCH (n:Document) RETURN n` 확인.
4. Swagger UI(`http://localhost:8000/docs`)에서 `GET /documents` 호출.
