# Spec 010: Knowledge Graph Construction

## 📋 Overview

**목표**: 현재 JSON으로만 저장되는 Entity를 Neo4j Graph로 구축하여 지식 베이스의 핵심 기능을 완성한다.

**문제 인식**:
-현재 `ExtractedMetadata.entities`가 JSON 문자열로 Document의 metadata 필드에 직렬화되어 저장됨
- Entity 간 관계 정보를 활용할 수 없음
- Graph 기반 쿼리가 불가능 (예: "Elon Musk가 언급된 모든 문서", "Tesla와 관련된 Technology 찾기")
- Spec 007에서 정의한 `TypedEntity`, `RelationshipType` 스키마가 실제로 활용되지 않음

**해결 방안**:
- Entity를 별도 Neo4j 노드로 생성 (`(:Entity)` label)
- Document-Entity 간 `MENTIONS` 관계 생성
- Entity 간 관계(WORKS_FOR, USES 등) 추출 및 저장 (향후 확장)
- Graph 탐색 API 제공

---

## 🎯 Goals

### Core Goals
1. **Entity 노드 생성**: ExtractedMetadata에서 추출된 Entity를 Neo4j 노드로 저장
2. **MENTIONS 관계 생성**: Document와 Entity 간 관계 구축
3. **Graph 조회 API**: Entity 기반 Document 검색 API 제공

### Stretch Goals (Optional)
4. **Entity 간 관계 추출**: LLM을 활용한 Entity 간 관계 추출 (WORKS_FOR, USES 등)
5. **Entity 중복 제거**: 동일 Entity 통합 (예: "Elon Musk" == "일론 머스크")

---

## 🔍 Current State

### 현재 Data Flow (Spec 005에서 구현됨)
```
1. 웹 페이지 스크래핑 → Markdown
2. LLM (Gemini 2.0 Flash) 메타데이터 추출 ← 여기서 Entity 추출!
   → ExtractedMetadata {
       entities: {
         "PERSON": ["Elon Musk"],
         "TECHNOLOGY": ["Tesla", "OpenAI"]
       }
     }
3. Neo4j 저장:
   - Document 노드 생성
   - metadata.entities가 JSON 문자열로 직렬화 ← 현재 상태
```

**⚠️ 중요: Spec 010의 범위**
- **LLM은 추가 호출하지 않습니다**
- 이미 Spec 005에서 추출된 Entity 데이터를 Graph로 구축하는 것이 목표
- Entity 간 관계(WORKS_FOR, USES 등)는 추출하지 않음 (향후 작업)

### 현재 Schema
```python
# app/domain/schemas/extraction.py
class ExtractedMetadata(BaseModel):
    entities: dict[EntityType, list[str]]
    # 예: {"PERSON": ["Elon Musk"], "TECHNOLOGY": ["Tesla"]}

# app/domain/schemas/ontology.py
class EntityType(str, Enum):
    PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, 
    LOCATION, EVENT, ACTIVITY

class TypedEntity(BaseModel):  # 현재 미사용
    name: str
    type: EntityType
    confidence: float = 1.0
```

### 현재 Neo4j 저장 로직
```python
# app/infrastructure/storage/neo4j.py (line 18-44)
def save(self, document: AtomicDocument):
    flattened_metadata = {}
    for key, value in document.metadata.items():
        if isinstance(value, (dict, list)):
            # entities가 JSON 문자열로 변환됨
            flattened_metadata[f"{key}_json"] = json.dumps(value)
```

---

## 🏗️ Proposed Architecture

### 새로운 Data Flow
```
1. 웹 페이지 스크래핑 → Markdown
2. LLM 메타데이터 추출 → ExtractedMetadata
3. Neo4j 저장:
   (a) Document 노드 생성
   (b) Entity 노드 생성/조회 (중복 체크)
   (c) (Document)-[:MENTIONS]->(Entity) 관계 생성
```

### Graph Schema
```cypher
# Document 노드 (기존)
(:Document {
  id: UUID,
  content: String,
  source_url: String,
  created_at: DateTime
})

# Entity 노드 (신규)
(:Entity {
  name: String,           # 예: "Elon Musk"
  type: String,           # EntityType (PERSON, ORGANIZATION 등)
  normalized_name: String # 검색용 정규화된 이름 (소문자)
})

# Document-Entity 관계 (신규)
(Document)-[:MENTIONS {
  count: Integer          # 문서 내 언급 횟수 (향후 확장)
}]->(Entity)
```

---

## 📦 Deliverables

### 1. Domain Layer
- [x] `EntityNode` 엔티티 클래스 추가 (선택: 필요시)
- [x] `GraphRepository` 인터페이스 정의 (Entity 저장/조회)

### 2. Infrastructure Layer
- [x] `Neo4jGraphRepository` 구현
  - `save_entity(name, type) -> Entity` - Entity 노드 생성/조회
  - `create_mention_relationship(doc_id, entity_name)`
  - `get_entities_by_document(doc_id) -> list[Entity]`
  - `get_documents_by_entity(entity_name) -> list[Document]`

### 3. Application/Use Case Layer
- [x] `IngestionService` 수정
  - Document 저장 후 Entity 그래프 구축 로직 추가

### 4. API Layer
- [x] `GET /entities` - 전체 Entity 목록 조회
- [x] `GET /entities/{name}/documents` - 특정 Entity가 언급된 Document 목록
- [x] `GET /documents/{id}/entities` - 특정 Document의 Entity 목록

### 5. Testing
- [x] Unit Tests: `Neo4jGraphRepository` 메서드 테스트
- [x] Integration Tests: Entity 그래프 구축 E2E 시나리오
- [x] Contract Tests: `GraphRepository` 인터페이스 계약 검증

---

## 🚨 Non-Goals (Out of Scope)

이번 Spec에서 다루지 **않는** 것들:

1. **Entity 간 관계 추출** (WORKS_FOR, USES 등) - **가장 중요한 향후 작업**
   - 현재: Document-Entity 관계(MENTIONS)만 구현
   - 향후 Spec: LLM을 활용한 Entity 간 관계 추출
   - 예시:
     ```
     "Elon Musk founded Tesla" 
     → (Elon Musk:PERSON)-[:FOUNDED]->(Tesla:ORGANIZATION)
     ```
   - **이것이 진정한 Knowledge Graph의 핵심**
   - 별도 LLM 프롬프트 및 관계 추출 로직 필요
   - **우선순위: High** (Phase 3 다음 작업으로 추천)

2. **Entity 중복 제거 (Deduplication)**
   - 동일 Entity 통합은 향후 작업
   - 현재는 name을 unique key로 사용
   - 예: "Apple" (회사) vs "apple" (과일) 구분 안 함

3. **Entity 신뢰도 (Confidence Score)**
   - `TypedEntity.confidence` 필드는 아직 활용 안 함
   - LLM이 Entity 분류 신뢰도를 함께 반환하지 않음

4. **외부 Knowledge Base 연동**
   - Wikipedia, Wikidata 등 외부 소스와 Entity 매칭
   - Entity 보강 (별칭, 설명 등)

---

## 🔮 Future Work (향후 계획)

### Phase 1: Entity Relationship Extraction (최우선)
- **Spec ???: Entity Relationship Extraction**
- LLM 프롬프트 개선하여 Entity 간 관계 추출
- 예: "X works for Y", "A uses B", "C founded D"
- RelationshipType 활용 (WORKS_FOR, FOUNDED, USES 등)
- **가치**: 진정한 Knowledge Graph 완성

### Phase 2: Entity Enrichment
- **Spec ???: Entity Deduplication & Normalization**
- 동일 Entity 통합
- 외부 KB 연동 (Wikipedia API)
- Entity 별칭 관리

### Phase 3: Advanced Querying
- **Spec ???: Graph Query API**
- Cypher 기반 복잡한 그래프 탐색
- "Elon Musk와 관련된 모든 Technology 찾기"
- Knowledge Path 분석

---

## 🔗 Dependencies

**Required**:
- Neo4j Driver (기존)
- Spec 007 Ontology 스키마 (`EntityType`, `RelationshipType`)

**Optional**:
- 없음

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Entity 이름 중복 (예: "Apple"이 회사/과일) | Medium | 향후 Disambiguation Spec 작성 |
| Large-scale Graph 성능 | Low | 현재 규모에서는 문제 없음, 향후 인덱스 최적화 |
| 기존 Document Entity 마이그레이션 | Medium | 마이그레이션 스크립트 작성 (선택) |

---

## 📝 Acceptance Criteria

1. ✅ Entity가 별도 Neo4j 노드로 저장됨
2. ✅ Document-Entity 간 MENTIONS 관계가 생성됨
3. ✅ `GET /entities/{name}/documents` API가 동작함
4. ✅ Integration Test 통과 (BDD 시나리오)
5. ✅ 기존 기능 (Document 저장/조회)에 영향 없음

---

## 🗓️ Timeline Estimate

- **Planning**: 1-2 시간
- **Implementation**: 4-6 시간
- **Testing**: 2-3 시간
- **Total**: 7-11 시간

---

## 📚 References

- [Spec 007: Ontology Design](../007-ontology-design/spec.md)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
