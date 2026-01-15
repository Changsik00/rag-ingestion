# Spec 002: Atomic Storage & Swagger Admin

## Goal
Neo4j(Graph DB)와 ChromaDB(Vector DB)를 연동하여, 수집된 데이터를 **Atomic Layer**(최소 단위 노드)로 저장하고 Swagger Admin을 통해 관리합니다.

## Tasks
- [ ] 데이터베이스 환경 설정 (`docker-compose.yml`)
  - [ ] Neo4j 컨테이너 구성 (apoc 플러그인 포함)
  - [ ] ChromaDB 컨테이너 구성
- [ ] 의존성 추가 (`pyproject.toml`)
  - [ ] `neo4j` (Driver)
  - [ ] `chromadb` (Client)
  - [ ] `langchain-community` (VectorStore 유틸리티 필요 시)
- [ ] Domain Layer 확장 (DDD 적용)
  - [ ] `AtomicDocument` Entity 정의 (app/domain/entities)
  - [ ] `Source` Value Object 정의 (app/domain/value_objects)
  - [ ] `DocumentRepository` 인터페이스 정의 (app/domain/interfaces)
- [ ] Infrastructure Layer 구현
  - [ ] `Neo4jStorage` 구현 (app/infrastructure/storage)
  - [ ] `ChromaStorage` 구현 (app/infrastructure/storage)
  - [ ] `CompositeStorage` 구현 (app/infrastructure/storage)
- [ ] Application Layer (Use Cases) 수정
  - [ ] `IngestionService`에 `save` 로직 추가
- [ ] Interface Layer (API) 수정
  - [ ] `POST /ingest/web`에서 저장 옵션 처리
  - [ ] `GET /documents` 엔드포인트 추가 (저장된 문서 목록 조회)
- [ ] 문서화 (Documentation)
  - [ ] `docs/architecture.md`: DDD 구조(Entity/VO/Storage) 반영 및 설계 근거 기술
- [ ] 테스트 및 검증
  - [ ] DB 연동 통합 테스트 (Test Containers 또는 Local Docker)
