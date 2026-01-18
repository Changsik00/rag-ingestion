# feat(spec-016): entity-entity relationship extraction

## 📋 요약

Knowledge Graph에 Entity 간 관계 추출 및 저장 기능을 구현하여 "Elon Musk가 Tesla를 FOUNDED" 또는 "Netflix가 Python을 USES"와 같은 의미적 연결을 가능하게 합니다. 이를 통해 Document-Entity 그래프가 진정한 Knowledge Graph로 전환됩니다.

**관련 문서**: [Spec 016](../specs/016-entity-relationship-extraction/spec.md) | [Walkthrough](../specs/016-entity-relationship-extraction/walkthrough.md)

---

## 🎯 동기

이 변경 이전에는 Entity가 `MENTIONS` 관계를 통해 문서에만 연결되었습니다. Entity에 대한 문서를 찾는 데는 유용하지만, Entity 간 관계는 포착하지 못했습니다.

**이제 지원되는 쿼리:**
- "Elon Musk가 설립한 회사는?"
- "Tesla가 사용하는 기술은?"
- "Google에서 일하는 사람은?"

이를 통해 더 정교한 그래프 탐색과 지식 발견이 가능합니다.

---

## 🔧 구현

### 1. Domain 개선

#### Entity Type 확장 (7개 → 9개)
[`app/domain/schemas/ontology.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/ontology.py#L13-L27)

더 나은 Entity 분류를 위해 `PRODUCT`와 `DOCUMENT` 타입 추가.

#### EntityRelationship Schema
[`app/domain/schemas/extraction.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/extraction.py#L23-L26)

```python
class EntityRelationship(BaseModel):
    source: str
    source_type: EntityType
    relationship: RelationshipType  # FOUNDED, WORKS_FOR, USES 등
    target: str
    target_type: EntityType
    confidence: float = Field(ge=0.0, le=1.0)
```

### 2. LLM Prompt 개선
[`app/infrastructure/llm/langchain_adapter.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/llm/langchain_adapter.py#L65-L79)

LLM 프롬프트에 관계 추출 지시사항과 예제 추가.

### 3. Neo4j 저장소

#### Cypher Query
[`app/infrastructure/storage/cypher_queries.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/cypher_queries.py#L71-L75)

```cypher
CREATE_ENTITY_RELATIONSHIP = """
MATCH (source:Entity {name: $source_name})
MATCH (target:Entity {name: $target_name})
MERGE (source)-[r:RELATIONSHIP {type: $relationship_type}]->(target)
RETURN r
"""
```

#### Repository 구현
[`app/infrastructure/storage/neo4j_graph_repository.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/neo4j_graph_repository.py#L69-L80)

- `create_entity_relationship()`
- `get_entity_relationships(entity_name, relationship_type=None)`

### 4. Ingestion Pipeline
[`app/use_cases/ingestion.py`](file:///Users/ck/Project/doit/rag-ingestion/app/use_cases/ingestion.py#L92-L113)

`_build_knowledge_graph()` 업데이트:
1. Entity 노드 + MENTIONS 생성 (기존)
2. ✨ **신규**: Entity-Entity RELATIONSHIP 엣지 생성
3. ✨ **신규**: 관계에서 누락된 Entity 처리
4. ✨ **신규**: 빈 Entity safety check

### 5. API Endpoint
[`app/interfaces/api/endpoints/entities.py`](file:///Users/ck/Project/doit/rag-ingestion/app/interfaces/api/endpoints/entities.py#L67-L72)

```http
GET /entities/{name}/relationships?relationship_type=FOUNDED
```

선택적 타입 필터링을 통해 Entity의 모든 관계를 반환합니다.

---

## ✅ 테스트

**신규 테스트**: 15개  
**전체 통과**: 92개

### Unit Tests
- [`test_entity_relationship.py`](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/domain/test_entity_relationship.py): EntityRelationship schema 검증
- [`test_neo4j_graph_repository.py`](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/test_neo4j_graph_repository.py#L160-L240): Repository 메서드

### Contract Tests
- [`test_graph_repository_contract.py`](file:///Users/ck/Project/doit/rag-ingestion/tests/contracts/test_graph_repository_contract.py#L32-L36): Protocol 준수

### BDD Integration Tests
- [`test_entity_relationships.py`](file:///Users/ck/Project/doit/rag-ingestion/tests/integration/bdd/test_entity_relationships.py): 3개 시나리오
  - ✅ Relationship API 조회
  - ✅ 타입 필터링
  - ✅ 잘못된 타입 처리

---

> [!WARNING]
> **Known Issues (Spec 016과 무관)**
> 
> ChromaDB embedding 설정으로 인한 4개 기존 integration test 실패:
> - `test_successful_entity_graph_auto_construction`
> - `test_entity_based_document_search`
> - `test_entity_deduplication`
> - `test_duplicate_url_sequential_ingestion`
> 
> **원인**: ChromaDB가 설치 시도에도 불구하고 `onnxruntime`을 찾지 못함  
> **영향**: Spec 016 기능에 영향 없음 (신규 테스트 15개 모두 통과)  
> **해결**: ChromaDB 환경 설정을 위한 별도 Spec 필요

---

## 🔄 Breaking Changes

없음. 순수 추가 기능:
- 기존 Entity 추출은 계속 작동
- `ExtractedMetadata`의 새 `relationships` 필드는 선택사항
- API는 하위 호환성 유지

---

## 📚 문서화

- ✅ [`docs/ontology.md`](file:///Users/ck/Project/doit/rag-ingestion/docs/ontology.md#L284-L324): 관계 구현 섹션 추가
- ✅ [`backlog/queue.md`](file:///Users/ck/Project/doit/rag-ingestion/backlog/queue.md#L94-L100): Spec 016 완료 표시
- ✅ Swagger UI: `/entities/{name}/relationships` 문서화

---

## 🧪 검증

```bash
# 서비스 시작
docker compose up -d

# 테스트 실행
uv run pytest tests/ -v -k "not (test_successful_entity_graph or test_entity_based or test_entity_deduplication or test_duplicate_url)"

# 예상 결과: 92 passed

# API 수동 테스트
curl http://localhost:8000/entities/Tesla/relationships
curl 'http://localhost:8000/entities/Elon%20Musk/relationships?relationship_type=FOUNDED'
```

---

## ☑️ PR Checklist

- [x] 코드가 프로젝트 구조를 따름 (Clean Architecture + DDD)
- [x] 모든 신규 코드에 unit test 있음 (15개 테스트 추가)
- [x] Integration test 추가됨 (3개 BDD 시나리오)
- [x] 문서 업데이트 (`ontology.md`, `backlog/queue.md`)
- [x] Breaking change 없음
- [x] Swagger 문서화 완료
- [x] Known issues 문서화
- [x] Commit이 semantic 형식 준수 (`feat:`, `fix:`, `docs:`)

---

**총 커밋 수**: 32  
**브랜치**: `feature/016-entity-relationship-extraction`  
**리뷰 준비**: ✅
