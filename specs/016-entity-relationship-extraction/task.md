# Task List: Spec 016 - Entity-Entity Relationship Extraction

## Progress

- [x] Spec 번호 확정 (016)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] Entity Type 확장 결정 (7개 → 9개, PRODUCT + DOCUMENT 추가)
- [x] 백로그 업데이트
- [x] 사용자 Plan Accept 완료
- [x] 브랜치 생성 및 구현 시작 → **9개 커밋 완료 (Task 1-7)**

---

## Task 1: 브랜치 생성 및 Spec 문서 커밋

- [x] 브랜치 생성: `git checkout -b feature/016-entity-relationship-extraction`
- [x] 브랜치 확인: `git branch --show-current`
- [x] Spec 문서 커밋: `git add specs/016-entity-relationship-extraction/ backlog/queue.md && git commit -m "docs: add spec 016 - entity relationship extraction"`

---

## Task 2: Entity Type 확장 (9개)

### 2-1. EntityType Enum 업데이트

- [x] `app/domain/schemas/ontology.py` 열기
- [x] `PRODUCT = "PRODUCT"` 추가
- [x] `DOCUMENT = "DOCUMENT"` 추가
- [x] Docstring 업데이트 (7개 → 9개)
- [x] 테스트: `pytest tests/contracts/test_storage_contract.py -v` (16 passed, 2 skipped)
- [x] 커밋: `feat: add PRODUCT and DOCUMENT entity types`

**커밋 메시지:**
```
feat: add PRODUCT and DOCUMENT entity types

- Add PRODUCT type for physical/digital products
- Add DOCUMENT type for papers, books, reports
- Total 9 entity types now
- CONCEPT serves as fallback for uncertain cases
```

### 2-2. LLM Prompt 업데이트

- [x] `app/infrastructure/llm/langchain_adapter.py` 열기
- [x] Prompt에 PRODUCT, DOCUMENT 설명 추가
- [x] "If uncertain → CONCEPT" fallback 규칙 추가
- [x] 테스트: `pytest tests/unit/test_usecases.py -v` (3 passed)
- [x] 커밋: `feat: update llm prompt with new entity types`

---

## Task 3: Domain Schema - EntityRelationship 추가

### 3-1. EntityRelationship 모델 정의

- [x] `app/domain/schemas/extraction.py` 열기
- [x] `EntityRelationship` 클래스 추가
- [x] Fields: source, source_type, relationship, target, target_type, confidence
- [x] 테스트: `pytest tests/unit/domain/ -v` (8 passed)
- [x] 커밋: `feat: add EntityRelationship domain schema`

### 3-2. ExtractedMetadata 확장

- [x] `ExtractedMetadata`에 `relationships: List[EntityRelationship]` 필드 추가
- [x] default_factory=list 설정
- [x] 테스트: 위와 동일
- [x] 커밋: 위와 통합

---

## Task 4: GraphRepository 인터페이스 확장

### 4-1. Protocol 메서드 추가

- [x] `app/domain/interfaces/graph_repository.py` 열기
- [x] `create_entity_relationship` 메서드 시그니처 추가
- [x] `get_entity_relationships` 메서드 시그니처 추가
- [x] Docstring 작성
- [x] 커밋: `feat: add relationship methods to GraphRepository protocol`

### 4-2. Contract Test 업데이트

- [x] `tests/contracts/test_graph_repository_contract.py` 열기
- [x] `test_has_create_entity_relationship` 추가
- [x] `test_has_get_entity_relationships` 추가
- [x] 테스트: `pytest tests/contracts/test_graph_repository_contract.py -v`
- [x] 커밋: `test: add contract tests for relationship methods`

---

## Task 5: Neo4j 구현 - Cypher Queries

### 5-1. Cypher Query Templates

- [x] `app/infrastructure/storage/cypher_queries.py` 열기
- [x] `CREATE_ENTITY_RELATIONSHIP` 쿼리 추가
- [x] `GET_ENTITY_RELATIONSHIPS` 쿼리 추가
- [x] `GET_ENTITY_RELATIONSHIPS_BY_TYPE` 쿼리 추가
- [x] 커밋: `feat: add cypher queries for entity relationships`

### 5-2. Neo4jGraphRepository 구현

- [x] `app/infrastructure/storage/neo4j_graph.py` 열기
- [x] `create_entity_relationship` 메서드 구현
- [x] `get_entity_relationships` 메서드 구현
- [x] Relationship type 동적 처리 (f-string 사용)
- [x] 테스트: `pytest tests/unit/test_neo4j_graph_repository.py -v`
- [x] 커밋: `feat: implement entity relationship methods in Neo4jGraphRepository`

---

## Task 6: LLM Prompt - Relationship 추출

### 6-1. Prompt 확장

- [x] `app/infrastructure/llm/langchain_adapter.py` 열기
- [x] Relationship 추출 지시 추가 (section 5)
- [x] Relationship 타입별 예시 추가 (FOUNDED, WORKS_FOR 등)
- [x] "Only EXPLICIT relationships" 강조
- [x] 커밋: `feat: add relationship extraction to llm prompt`

**Note:** Task 6-2 (Pydantic 출력 스키마)는 Task 3에서 이미 완료됨

---

## Task 7: IngestionService 통합

### 7-1. _build_knowledge_graph 확장

- [x] `app/use_cases/ingestion.py` 열기
- [x] Entity-Entity Relationship 처리 로직 추가
- [x] Source/Target Entity 존재 확인 및 생성
- [x] `create_entity_relationship` 호출
- [x] Low confidence 관계 로깅 추가
- [x] 메서드 시그니처 변경 (entities → semantic_data)
- [x] 커밋: `feat: integrate entity relationships in ingestion service`

---

## Task 8: API - Relationship 조회

### 8-1. 엔드포인트 추가

- [x] `app/interfaces/api/endpoints/entities.py` 열기
- [x] `GET /entities/{entity_name}/relationships` 추가
- [x] Query parameter: relationship_type (Optional)
- [x] Response model 정의
- [x] Docstring 및 예시 작성
- [x] RelationshipType enum validation 추가
- [x] 커밋: `feat: add entity relationships api endpoint`

### 8-2. Swagger 문서 확인

- [ ] 서버 실행: `docker compose up`
- [ ] Swagger 확인: http://localhost:8000/docs
- [ ] 새 엔드포인트 표시 확인
- [ ] Example response 확인

---

## Task 9: Unit Tests

### 9-1. Domain Schema Tests

- [ ] `tests/unit/domain/test_entity_relationship.py` 생성
- [ ] EntityRelationship 검증 테스트
- [ ] Confidence 범위 테스트 (0.0 ~ 1.0)
- [ ] 테스트: `pytest tests/unit/domain/ -v`
- [ ] 커밋: `test: add unit tests for EntityRelationship schema`

### 9-2. Repository Tests

- [ ] `tests/unit/test_neo4j_graph_repository.py` 업데이트
- [ ] `test_create_entity_relationship` 추가
- [ ] `test_get_entity_relationships` 추가
- [ ] Mock driver 검증
- [ ] 테스트: `pytest tests/unit/test_neo4j_graph_repository.py -v`
- [ ] 커밋: `test: add unit tests for relationship methods`

---

## Task 10: Integration Tests (BDD)

### 10-1. BDD Scenario 작성

- [ ] `tests/integration/bdd/test_entity_relationships.py` 생성
- [ ] Scenario 1: Relationship 추출 및 저장
- [ ] Scenario 2: Relationship API 조회
- [ ] Scenario 3: Relationship 타입별 필터링
- [ ] Given-When-Then 구조
- [ ] 커밋: `test: add bdd tests for entity relationships`

### 10-2. Integration Test 실행

- [ ] Docker Compose 실행: `docker compose up -d`
- [ ] 테스트: `pytest tests/integration/bdd/test_entity_relationships.py -v`
- [ ] 결과 확인 (예상: 3 passed)
- [ ] Docker 종료: `docker compose down`

---

## Task 11: 전체 테스트 및 검증

### 11-1. 전체 테스트 실행

- [ ] `pytest tests/ -v`
- [ ] 회귀 확인 (기존 85 passed 유지)
- [ ] 신규 테스트 통과 확인
- [ ] 실패 시 수정

### 11-2. Neo4j Browser 검증

- [ ] Neo4j Browser 접속: http://localhost:7474
- [ ] Cypher 쿼리: `MATCH (s:Entity)-[r]->(t:Entity) RETURN s, r, t LIMIT 20`
- [ ] Relationship 시각화 확인 (FOUNDED, WORKS_FOR 등)
- [ ] Screenshot 저장 (선택사항)

### 11-3. API 수동 테스트

- [ ] Swagger UI: http://localhost:8000/docs
- [ ] `POST /ingest/web` 테스트 (관계 포함 문서)
- [ ] `GET /entities/{name}/relationships` 테스트
- [ ] Response 검증

---

## Task 12: Documentation 업데이트

### 12-1. docs/ontology.md 업데이트

- [ ] PRODUCT, DOCUMENT 타입 설명 추가
- [ ] Entity Type 개수 7 → 9로 수정
- [ ] Relationship 타입 활용 예시 추가
- [ ] 커밋: `docs: update ontology.md with new entity types`

### 12-2. Backlog 업데이트

- [ ] Spec 016 완료 표시
- [ ] 커밋: `docs: mark spec 016 as completed in backlog`

---

## Task 13: PR 준비 및 생성

- [ ] `specs/016-entity-relationship-extraction/walkthrough.md` 작성
- [ ] `specs/016-entity-relationship-extraction/pr_description.md` 작성
- [ ] Push: `git push origin feature/016-entity-relationship-extraction`
- [ ] PR 생성:
```bash
gh pr create --base main --head feature/016-entity-relationship-extraction \
  --title "feat(spec-016): entity-entity relationship extraction" \
  --body-file specs/016-entity-relationship-extraction/pr_description.md
```

---

## Summary

**총 Task**: 13개
1. ✅ 브랜치 생성 및 Spec 문서 커밋
2. ⏳ Entity Type 확장 (2 subtasks)
3. ⏳ Domain Schema - EntityRelationship (2 subtasks)
4. ⏳ GraphRepository 인터페이스 (2 subtasks)
5. ⏳ Neo4j 구현 (2 subtasks)
6. ⏳ LLM Prompt 업데이트 (2 subtasks)
7. ⏳ IngestionService 통합
8. ⏳ API 엔드포인트 (2 subtasks)
9. ⏳ Unit Tests (2 subtasks)
10. ⏳ Integration Tests (2 subtasks)
11. ⏳ 전체 테스트 및 검증 (3 subtasks)
12. ⏳ Documentation (2 subtasks)
13. ⏳ PR 준비

**예상 커밋 수**: 10-12개
**예상 소요 시간**: 4-6시간
