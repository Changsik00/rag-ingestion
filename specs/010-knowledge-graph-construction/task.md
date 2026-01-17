# Task Checklist: Spec 010 - Knowledge Graph Construction

## Progress

- [x] Spec 번호 확정 (010)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 사용자 승인 완료
- [x] 브랜치 생성 및 구현 시작

---

## Task 1: 브랜치 생성 및 준비

- [x] 브랜치 생성: `git checkout -b feature/010-knowledge-graph-construction`
- [x] spec.md, plan.md, task.md 커밋
- [x] 커밋: `docs: add spec 010 - knowledge graph construction`

---

## Task 2: Domain Layer - GraphRepository 인터페이스

- [x] `app/domain/interfaces/graph_repository.py` 생성
  - [x] `save_entity(name, type)` 메서드 정의
  - [x] `create_mention_relationship(doc_id, entity_name)` 메서드 정의
  - [x] `get_entities_by_document(doc_id)` 메서드 정의
  - [x] `get_document_ids_by_entity(entity_name)` 메서드 정의
  - [x] `list_all_entities(limit)` 메서드 정의

---

## Task 3: Infrastructure Layer - Cypher Query Templates

- [x] `app/infrastructure/storage/cypher_queries.py` 생성
  - [x] `MERGE_ENTITY` 쿼리 템플릿
  - [x] `CREATE_ENTITY_INDEX` 쿼리 템플릿
  - [x] `CREATE_MENTIONS_RELATIONSHIP` 쿼리 템플릿
  - [x] `GET_ENTITIES_BY_DOCUMENT` 쿼리 템플릿
  - [x] `GET_DOCUMENT_IDS_BY_ENTITY` 쿼리 템플릿
  - [x] `LIST_ALL_ENTITIES` 쿼리 템플릿
- [x] 커밋: `feat: add GraphRepository interface and Cypher query templates`

---

## Task 4: Infrastructure Layer - Neo4jGraphRepository 구현

- [x] `app/infrastructure/storage/neo4j_graph.py` 생성
  - [x] `cypher_queries` 모듈 import
  - [x] `__init__` 및 인덱스 생성 로직
  - [x] `save_entity` 구현 (MERGE 로직)
  - [x] `create_mention_relationship` 구현
  - [x] `get_entities_by_document` 구현
  - [x] `get_document_ids_by_entity` 구현
  - [x] `list_all_entities` 구현
- [ ] 커밋 대기: `feat: implement Neo4jGraphRepository`

---

## Task 5: Application Layer - IngestionService 수정

- [x] `app/use_cases/ingestion.py` 수정
  - [x] GraphRepository 생성자 파라미터 추가
  - [x] `_build_knowledge_graph` 메서드 추가
  - [x] `process_job` 메서드에서 Entity 그래프 구축 호출
- [ ] 커밋 대기: `feat: integrate knowledge graph building in ingestion`

---

## Task 6: Dependency Injection - GraphRepository 추가

- [ ] `app/interfaces/api/dependencies.py` 수정
  - [ ] `get_graph_repository()` 함수 추가
  - [ ] `get_ingestion_service()`에 GraphRepository 주입
- [ ] 커밋: `feat: add GraphRepository dependency injection`

---

## Task 7: API Layer - Entity 엔드포인트

- [ ] `app/interfaces/api/endpoints/entities.py` 생성
  - [ ] `GET /entities` - 전체 Entity 목록
  - [ ] `GET /entities/{name}/documents` - Entity별 Document 목록
  - [ ] `GET /entities/{name}/info` - Entity 정보
- [ ] `app/interfaces/api/main.py` 수정
  - [ ] entities router 추가
- [ ] 커밋: `feat: add entity API endpoints`

---

## Task 8: Unit Tests - Neo4jGraphRepository

- [ ] `tests/unit/test_neo4j_graph_repository.py` 생성
  - [ ] `test_save_entity_creates_node`
  - [ ] `test_save_entity_merge_duplicates`
  - [ ] `test_create_mention_relationship`
  - [ ] `test_get_entities_by_document`
  - [ ] `test_get_document_ids_by_entity`
  - [ ] `test_list_all_entities`
- [ ] 테스트 실행: `uv run pytest tests/unit/test_neo4j_graph_repository.py -v`
- [ ] 커밋: `test: add unit tests for Neo4jGraphRepository`

---

## Task 9: Integration Tests (BDD) - Knowledge Graph

- [ ] `tests/integration/bdd/test_knowledge_graph.py` 생성
  - [ ] `test_successful_entity_graph_auto_construction` - Entity 자동 구축
  - [ ] `test_entity_based_document_search` - Entity로 Document 검색
  - [ ] `test_entity_deduplication` - Entity 중복 처리
- [ ] 테스트 실행: `docker compose up -d && uv run pytest tests/integration/bdd/test_knowledge_graph.py -v -m integration`
- [ ] 커밋: `test: add integration tests for knowledge graph`

---

## Task 10: Contract Tests - GraphRepository

- [ ] `tests/contracts/test_graph_repository_contract.py` 생성
  - [ ] GraphRepository 인터페이스 검증
  - [ ] Neo4jGraphRepository 계약 준수 확인
- [ ] 테스트 실행: `uv run pytest tests/contracts/test_graph_repository_contract.py -v`
- [ ] 커밋: `test: add contract tests for GraphRepository`

---

## Task 11: 전체 테스트 실행 및 검증

- [ ] Contract Tests: `uv run pytest tests/contracts/ -v`
- [ ] Unit Tests: `uv run pytest tests/unit/ -v`
- [ ] Integration Tests: `docker compose up -d && uv run pytest tests/integration/ -v -m integration`
- [ ] 모든 테스트 통과 확인
- [ ] 기존 기능 영향 여부 확인

---

## Task 12: PR 준비 및 문서화

- [ ] `specs/010-knowledge-graph-construction/pr_description.md` 작성
- [ ] 모든 변경사항 커밋
- [ ] 푸시: `git push origin feature/010-knowledge-graph-construction`
- [ ] PR 생성: `gh pr create --title "feat(spec-010): knowledge graph construction" --body-file specs/010-knowledge-graph-construction/pr_description.md`

---

## Notes

- Entity 노드는 `(:Entity)` label 사용
- Document-Entity 관계는 `[:MENTIONS]` 사용
- Entity.name을 unique constraint로 설정
- 기존 Document 기능에 영향 없도록 주의
