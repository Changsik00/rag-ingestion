# Implementation Plan: Spec 016 - Entity-Entity Relationship Extraction

## 📋 Branch Strategy

```bash
feature/016-entity-relationship-extraction
```

**Single commit per task** 원칙 준수

---

## 🎯 Core Strategy

### 1. Entity Type 확장 결정

**제안: 7개 유지 (현재 단계에서)**

**근거:**
1. Entity-Entity Relationship 추출이 핵심 목표
2. 실전 데이터 없이 타입 추가는 리스크
3. 사용 후 confidence 낮은 케이스 분석하고 다음 Spec에서 확장

**만약 확장한다면:**
- PRODUCT (제품)
- DOCUMENT (논문, 책)
추가하여 총 9개

**최종 결정:** 사용자 승인 필요 ⚠️

---

### 2. 3-Phase Approach

**Phase 1: Domain Schema 확장**
- `EntityRelationship` 모델 추가
- `ExtractedMetadata`에 relationships 필드 추가

**Phase 2: LLM & Graph Repository**
- LLM Prompt에 relationship 추출 추가
- `GraphRepository`에 relationship 메서드 추가
- Neo4j 구현

**Phase 3: API & Integration**
- Relationship 조회 API
- IngestionService 통합
- 테스트 작성

---

## 📂 Proposed Changes

### 1. Domain Layer

#### [MODIFY] [`app/domain/schemas/extraction.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/extraction.py)

**추가 내용:**
```python
class EntityRelationship(BaseModel):
    """LLM이 추출한 Entity 간 관계"""
    source: str = Field(description="Source entity name")
    source_type: EntityType = Field(description="Source entity type")
    relationship: RelationshipType = Field(description="Relationship type")
    target: str = Field(description="Target entity name")
    target_type: EntityType = Field(description="Target entity type")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class ExtractedMetadata(BaseModel):
    # 기존 필드
    ...
    # 🆕 신규 필드
    relationships: List[EntityRelationship] = Field(
        default_factory=list,
        description="Entity 간 관계"
    )
```

#### [MODIFY] [`app/domain/interfaces/graph_repository.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/interfaces/graph_repository.py)

**추가 메서드:**
```python
def create_entity_relationship(
    self,
    source_name: str,
    relationship_type: RelationshipType,
    target_name: str
) -> None:
    """Entity 간 관계 생성"""
    ...

def get_entity_relationships(
    self,
    entity_name: str,
    relationship_type: Optional[RelationshipType] = None
) -> List[Dict[str, Any]]:
    """Entity의 모든 관계 조회"""
    ...
```

---

### 2. Infrastructure Layer

#### [MODIFY] [`app/infrastructure/storage/cypher_queries.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/cypher_queries.py)

**추가 쿼리:**
```python
# Entity-Entity Relationship 생성
CREATE_ENTITY_RELATIONSHIP = """
MATCH (source:Entity {name: $source_name})
MATCH (target:Entity {name: $target_name})
MERGE (source)-[r:{relationship_type}]->(target)
ON CREATE SET r.created_at = datetime()
"""

# Entity Relationship 조회
GET_ENTITY_RELATIONSHIPS = """
MATCH (e:Entity {name: $entity_name})-[r]->(target:Entity)
RETURN type(r) as relationship_type, 
       target.name as target_name,
       target.type as target_type
"""
```

#### [MODIFY] [`app/infrastructure/storage/neo4j_graph.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/neo4j_graph.py)

**신규 메서드 구현:**
```python
def create_entity_relationship(
    self, 
    source_name: str, 
    relationship_type: RelationshipType, 
    target_name: str
) -> None:
    """Entity 간 관계 생성"""
    with self.driver.session() as session:
        # Cypher 쿼리 포맷팅 주의 (relationship_type은 동적)
        query = f"""
        MATCH (source:Entity {{name: $source_name}})
        MATCH (target:Entity {{name: $target_name}})
        MERGE (source)-[r:{relationship_type.value}]->(target)
        ON CREATE SET r.created_at = datetime()
        """
        session.run(
            query,
            source_name=source_name,
            target_name=target_name
        )
```

#### [MODIFY] [`app/infrastructure/llm/langchain_adapter.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/llm/langchain_adapter.py)

**Prompt 업데이트:**
```python
prompt = f"""
Extract the following information:

1. Title
2. Summary (3 sentences)
3. Keywords (5-10)
4. Entities (PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, LOCATION, EVENT, ACTIVITY)

5. Relationships between entities:
   - FOUNDED: Person founded Organization
   - WORKS_FOR: Person works for Organization  
   - USES: Organization uses Technology
   - RELATED_TO: Concept related to Concept
   - SUPPORTS: Technology supports Activity
   - PERFORMED: Person performed Activity
   - PART_OF: Activity is part of Activity

Only extract relationships that are EXPLICITLY mentioned.
Do NOT infer or assume relationships.

Output format:
{{
  "relationships": [
    {{
      "source": "Entity name",
      "source_type": "PERSON|ORGANIZATION|...",
      "relationship": "FOUNDED|WORKS_FOR|...",
      "target": "Entity name",
      "target_type": "PERSON|ORGANIZATION|..."
    }}
  ]
}}
"""
```

**Pydantic 출력 스키마 업데이트:**
```python
# relationships 필드 추가
```

---

### 3. Use Cases Layer

#### [MODIFY] [`app/use_cases/ingestion.py`](file:///Users/ck/Project/doit/rag-ingestion/app/use_cases/ingestion.py)

**`_build_knowledge_graph` 메서드 확장:**
```python
def _build_knowledge_graph(self, doc_id: str, semantic_data: ExtractedMetadata):
    """Knowledge Graph 구축"""
    
    # 1. Entity 저장 + Document-Entity MENTIONS 관계 (기존)
    all_entity_names = set()
    for entity_type, names in semantic_data.entities.items():
        for name in names:
            self.graph.save_entity(name, entity_type)
            self.graph.create_mention_relationship(doc_id, name)
            all_entity_names.add(name)
    
    # 🆕 2. Entity-Entity Relationship (신규)
    for rel in semantic_data.relationships:
        # 2-1. Source/Target Entity 존재 확인 및 생성
        if rel.source not in all_entity_names:
            self.graph.save_entity(rel.source, rel.source_type)
            all_entity_names.add(rel.source)
        
        if rel.target not in all_entity_names:
            self.graph.save_entity(rel.target, rel.target_type)
            all_entity_names.add(rel.target)
        
        # 2-2. Relationship 생성
        self.graph.create_entity_relationship(
            source_name=rel.source,
            relationship_type=rel.relationship,
            target_name=rel.target
        )
```

---

### 4. API Layer

#### [MODIFY] [`app/interfaces/api/endpoints/entities.py`](file:///Users/ck/Project/doit/rag-ingestion/app/interfaces/api/endpoints/entities.py)

**신규 엔드포인트:**
```python
@router.get("/{entity_name}/relationships", response_model=List[Dict[str, Any]])
def get_entity_relationships(
    entity_name: str,
    relationship_type: Optional[str] = Query(None),
    graph: GraphRepository = Depends(get_graph_repository)
):
    """
    특정 Entity의 관계 조회
    
    **Example:**
    ```
    GET /entities/Elon%20Musk/relationships
    ```
    
    **Response:**
    ```json
    [
      {
        "relationship_type": "FOUNDED",
        "target_name": "Tesla",
        "target_type": "ORGANIZATION"
      }
    ]
    ```
    """
    rel_type = RelationshipType(relationship_type) if relationship_type else None
    return graph.get_entity_relationships(entity_name, rel_type)
```

---

### 5. Tests

#### [NEW] `tests/unit/test_entity_relationship.py`

**Unit Tests (Domain):**
```python
def test_entity_relationship_schema():
    """EntityRelationship 스키마 검증"""
    rel = EntityRelationship(
        source="Elon Musk",
        source_type=EntityType.PERSON,
        relationship=RelationshipType.FOUNDED,
        target="Tesla",
        target_type=EntityType.ORGANIZATION
    )
    assert rel.source == "Elon Musk"
```

#### [MODIFY] `tests/unit/test_neo4j_graph_repository.py`

**추가 테스트:**
```python
def test_create_entity_relationship(mock_driver):
    """Entity-Entity Relationship 생성 테스트"""
    # Given
    graph = Neo4jGraphRepository(mock_driver)
    
    # When
    graph.create_entity_relationship(
        source_name="Elon Musk",
        relationship_type=RelationshipType.FOUNDED,
        target_name="Tesla"
    )
    
    # Then
    mock_driver.session().run.assert_called_once()
```

#### [MODIFY] `tests/contracts/test_graph_repository_contract.py`

**Contract Test 추가:**
```python
def test_graph_repository_has_create_entity_relationship(repository_class):
    """GraphRepository는 create_entity_relationship 메서드를 가져야 함"""
    assert hasattr(repository_class, 'create_entity_relationship')
```

#### [NEW] `tests/integration/bdd/test_entity_relationships.py`

**Integration Test (BDD):**
```python
@pytest.mark.integration
def test_entity_relationship_extraction_and_storage():
    """
    Given: 관계가 명시된 문서를 수집하고
    When: LLM이 Entity-Entity 관계를 추출하면
    Then: Neo4j에 관계가 저장된다
    """
    # Given
    url = "https://example.com/tech-article"
    # 내용: "Elon Musk founded Tesla..."
    
    # When
    response = client.post("/ingest/web", json={
        "url": url,
        "enable_extraction": True
    })
    job_id = response.json()["job_id"]
    wait_for_job_completion(job_id)
    
    # Then - Entity Relationship 확인
    relationships = client.get("/entities/Elon Musk/relationships").json()
    assert any(
        r["relationship_type"] == "FOUNDED" and r["target_name"] == "Tesla"
        for r in relationships
    )
```

---

## 🧪 Verification Plan

### 1. Unit Tests

```bash
# Domain Schema 테스트
uv run pytest tests/unit/test_entity_relationship.py -v

# Graph Repository 테스트  
uv run pytest tests/unit/test_neo4j_graph_repository.py::test_create_entity_relationship -v
```

**예상 결과:** 신규 테스트 모두 통과

---

### 2. Contract Tests

```bash
# GraphRepository Protocol 준수 검증
uv run pytest tests/contracts/test_graph_repository_contract.py -v
```

**예상 결과:** Neo4jGraphRepository가 신규 메서드 구현 확인

---

### 3. Integration Tests (Docker 필요)

```bash
# Docker Compose 실행
docker compose up -d

# Integration Test 실행
uv run pytest tests/integration/bdd/test_entity_relationships.py -v
```

**예상 결과:** Entity-Entity Relationship이 Neo4j에 저장되고 API로 조회 가능

---

### 4. Manual Verification (Neo4j Browser)

```bash
# Neo4j Browser 접속
open http://localhost:7474

# Cypher 쿼리
MATCH (source:Entity)-[r]->(target:Entity)
RETURN source.name, type(r), target.name
LIMIT 20
```

**예상 결과:** FOUNDED, WORKS_FOR 등의 관계가 시각화됨

---

### 5. API Test (Swagger)

```bash
# Swagger UI 접속
open http://localhost:8000/docs

# GET /entities/{entity_name}/relationships 테스트
# entity_name: "Elon Musk"
```

**예상 결과:** Tesla, SpaceX 등과의 관계 반환

---

## 🚨 User Review Required

> [!WARNING]  
> **Entity Type 확장 결정 필요**
>
> **Option 1 (추천):** 현재 7개 유지, 사용 후 확장  
> **Option 2:** PRODUCT, DOCUMENT 추가 (총 9개)
>
> 어떤 옵션으로 진행할지 결정 부탁드립니다.

---

## ✅ Definition of Done

- [x] `EntityRelationship` 스키마 정의
- [x] LLM Prompt에 relationship 추출 추가
- [x] `GraphRepository.create_entity_relationship` 구현
- [x] `GET /entities/{name}/relationships` API 추가
- [x] Unit Tests 작성 및 통과
- [x] Contract Tests 통과
- [x] Integration Tests 통과
- [x] Neo4j Browser로 관계 시각화 확인
- [x] 기존 테스트 회귀 없음 (85 passed 유지)

---

**작성일:** 2026-01-19  
**예상 커밋 수:** 8-10개  
**예상 소요 시간:** 4-6시간
