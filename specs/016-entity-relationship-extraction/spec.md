# Spec 016: Entity-Entity Relationship Extraction

## 📋 개요

Spec 010에서 Document-Entity 관계(MENTIONS)를 구축했습니다. 이제 **Entity 간 관계**를 추출하여 진정한 Knowledge Graph를 완성합니다.

**현재 상태:**
```cypher
(Document)-[:MENTIONS]->(Entity:PERSON {name: "Elon Musk"})
(Document)-[:MENTIONS]->(Entity:ORGANIZATION {name: "Tesla"})
```

**목표 상태:**
```cypher
(Elon Musk:Entity)-[:FOUNDED]->(Tesla:Entity)
(Elon Musk:Entity)-[:WORKS_FOR]->(SpaceX:Entity)
(Tesla:Entity)-[:USES]->(Python:Entity)
```

---

## 🎯 목표

### 1. LLM 기반 Relationship 추출
- Prompt에 Entity 간 관계 추출 지시 추가
- 추출된 관계를 구조화된 데이터로 반환

### 2. Neo4j에 Relationship 저장
- `GraphRepository`에 relationship 생성 메서드 추가
- Cypher Query로 Entity-Entity 관계 생성

### 3. Relationship API 개발
- 특정 Entity의 관계 조회 API
- Relationship 타입별 필터링

### 4. Entity Type 확장 검토 (Optional)
- 현재 7개 → PRODUCT, DOCUMENT 추가 (총 9개)
- LLM Prompt 업데이트

---

## 🔍 상세 요구사항

### 1. LLM Prompt 업데이트

**현재 (Spec 005):**
```python
"Extract the following from the text:
- Title
- Summary
- Keywords
- Entities (PERSON, ORGANIZATION, TECHNOLOGY...)"
```

**변경 후:**
```python
"Extract the following:
...
- Entities with types
- Relationships between entities:
  * FOUNDED: Person founded Organization
  * WORKS_FOR: Person works for Organization
  * USES: Organization uses Technology
  * RELATED_TO: Concept related to Concept
  * ..."
```

**출력 형식:**
```json
{
  "relationships": [
    {
      "source": "Elon Musk",
      "source_type": "PERSON",
      "relationship": "FOUNDED",
      "target": "Tesla",
      "target_type": "ORGANIZATION"
    }
  ]
}
```

---

### 2. Domain Schema 확장

**`app/domain/schemas/extraction.py` 업데이트:**

```python
class EntityRelationship(BaseModel):
    """Entity 간 관계"""
    source: str
    source_type: EntityType
    relationship: RelationshipType
    target: str
    target_type: EntityType
    confidence: float = 1.0

class ExtractedMetadata(BaseModel):
    # 기존 필드
    title: Optional[str]
    summary: Optional[str]
    keywords: List[str]
    entities: Dict[EntityType, List[str]]
    
    # 새 필드
    relationships: List[EntityRelationship] = []  # 🆕
```

---

### 3. GraphRepository 메서드 추가

**`app/domain/interfaces/graph_repository.py`:**

```python
class GraphRepository(Protocol):
    # 기존 메서드
    def save_entity(self, ...) -> str: ...
    def create_mention_relationship(self, ...) -> None: ...
    
    # 🆕 신규 메서드
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
    ) -> List[EntityRelationship]:
        """특정 Entity의 관계 조회"""
        ...
```

---

### 4. Neo4j 구현

**`app/infrastructure/storage/neo4j_graph.py`:**

```cypher
# Entity-Entity 관계 생성
MATCH (source:Entity {name: $source_name})
MATCH (target:Entity {name: $target_name})
MERGE (source)-[r:FOUNDED]->(target)
ON CREATE SET r.created_at = datetime()
```

---

### 5. Ingestion Service 업데이트

**`app/use_cases/ingestion.py`:**

```python
def _build_knowledge_graph(self, doc_id: str, semantic_data: ExtractedMetadata):
    # 기존: Entity 저장 + MENTIONS 관계
    for entity_type, names in semantic_data.entities.items():
        for name in names:
            self.graph.save_entity(name, entity_type)
            self.graph.create_mention_relationship(doc_id, name)
    
    # 🆕 신규: Entity-Entity 관계
    for rel in semantic_data.relationships:
        self.graph.create_entity_relationship(
            source_name=rel.source,
            relationship_type=rel.relationship,
            target_name=rel.target
        )
```

---

### 6. API 엔드포인트

**`app/interfaces/api/endpoints/entities.py`:**

```python
@router.get("/{entity_name}/relationships")
def get_entity_relationships(
    entity_name: str,
    relationship_type: Optional[str] = None
) -> List[EntityRelationship]:
    """
    특정 Entity의 관계 조회
    
    Example: GET /entities/Elon Musk/relationships
    Returns: [
        {"source": "Elon Musk", "relationship": "FOUNDED", "target": "Tesla"}
    ]
    """
    ...
```

---

## 📐 범위

### In-Scope
✅ LLM Prompt에 relationship 추출 추가
✅ Entity-Entity 관계를 Neo4j에 저장
✅ Relationship 조회 API
✅ Entity Type 확장 검토 (PRODUCT, DOCUMENT 추가 여부)

### Out-of-Scope
❌ Relationship 자동 추론 (LLM이 명시적으로 추출한 것만)
❌ Relationship 신뢰도 검증 (향후 Logic Resolver에서)
❌ 복잡한 Graph 탐색 (Shortest Path 등)

---

## 🚨 주의사항

### 1. Entity 누락 문제
**문제:** Relationship에 언급된 Entity가 entities에 없을 수 있음

**해결:**
```python
# Relationship 저장 전 Entity 존재 확인
if rel.source not in all_entity_names:
    self.graph.save_entity(rel.source, rel.source_type)
```

### 2. LLM Hallucination
**문제:** LLM이 존재하지 않는 관계 생성

**완화:**
- Prompt에 "Only extract relationships explicitly mentioned" 명시
- confidence 낮은 관계는 로깅만

---

## ✅ Success Criteria

1. ✅ `EntityRelationship` 스키마 정의
2. ✅ LLM Prompt가 relationship 추출
3. ✅ `create_entity_relationship` 메서드 구현
4. ✅ Entity-Entity 관계가 Neo4j에 저장됨
5. ✅ `GET /entities/{name}/relationships` API 동작
6. ✅ 기존 테스트 통과 + 신규 테스트 작성

---

## 🔮 향후 확장

- **Logic Resolver:** Relationship 모순 탐지
- **Relationship 가중치:** 언급 빈도 기반
- **Multi-hop Query:** "Elon Musk와 2단계 이내 연결된 Technology는?"

---

**작성일:** 2026-01-19  
**우선순위:** High  
**예상 소요:** 4-6시간
