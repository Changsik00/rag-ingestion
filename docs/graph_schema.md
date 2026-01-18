# Neo4j Graph Schema 설명 (Spec 010)

## 🎯 목적

Spec 005에서 JSON 문자열로 저장되던 Entity를 Spec 010에서 Neo4j Graph 노드로 분리하여 구조화

---

## 📊 Before vs After

### Before (Spec 005): JSON 직렬화 방식

```cypher
# Document 노드만 존재
(:Document {
  id: "doc-123",
  content: "Elon Musk founded Tesla...",
  metadata: {
    entities_json: '{"PERSON": ["Elon Musk"], "ORGANIZATION": ["Tesla"]}'
  }
})
```

**문제점:**
- ❌ Entity 검색 어려움 (JSON 파싱 필요)
- ❌ Entity 간 관계 표현 불가
- ❌ Graph 쿼리 불가능
- ❌ Entity 중복 관리 어려움

---

### After (Spec 010): Graph 노드 분리

**3개의 분리된 구조:**

#### 1️⃣ Document 노드 (기존)
```cypher
(:Document {
  id: "doc-123",
  content: "Elon Musk founded Tesla...",
  metadata: {...}  # entities는 이제 별도 노드로!
})
```

#### 2️⃣ Entity 노드 (신규!)
```cypher
(:Entity {
  name: "Elon Musk",              # 원본 이름
  type: "PERSON",                 # EntityType (PERSON, ORGANIZATION 등)
  normalized_name: "elon musk",   # 검색용 정규화 (소문자)
  created_at: datetime()
})
```

**Entity 속성 설명:**
- `name`: Entity 원본 이름 (LLM이 추출한 그대로)
- `type`: EntityType enum 값 (PERSON, ORGANIZATION, TECHNOLOGY 등)
- `normalized_name`: 검색 최적화를 위한 소문자 변환 (예: `toLower($name)`)
- `created_at`: Entity 노드 생성 시각

#### 3️⃣ MENTIONS 관계 (신규!)
```cypher
(Document)-[:MENTIONS {
  created_at: datetime()          # 관계 생성 시각
}]->(Entity)
```

**MENTIONS 관계 속성:**
- `created_at`: 이 Document에서 Entity를 언급한 관계가 생성된 시각

---

## 🔍 시각화 비교

### Before: JSON 내장 방식
```
┌──────────────────────────────┐
│        Document              │
│   id: "doc-123"              │
│   content: "Elon Musk..."    │
│   metadata: {                │
│     entities_json:           │ ← JSON 문자열
│     '{"PERSON":              │
│       ["Elon Musk"],         │
│      "ORGANIZATION":          │
│       ["Tesla"]}'            │
│   }                          │
└──────────────────────────────┘
```

### After: Graph 노드 분리
```
┌─────────────────┐            ┌──────────────────────┐
│   Document      │            │      Entity          │
│  id: "doc-123"  │            │  name: "Elon Musk"   │
│  content: "..." │            │  type: "PERSON"      │
└─────────────────┘            │  normalized_name:    │
        │                      │   "elon musk"        │
        │                      └──────────────────────┘
        │                               ▲
        └─────[:MENTIONS]───────────────┘
           created_at: datetime()

┌─────────────────┐            ┌──────────────────────┐
│   Document      │            │      Entity          │
│  id: "doc-123"  │            │  name: "Tesla"       │
│  content: "..." │            │  type: "ORGANIZATION"│
└─────────────────┘            │  normalized_name:    │
        │                      │   "tesla"            │
        │                      └──────────────────────┘
        │                               ▲
        └─────[:MENTIONS]───────────────┘
           created_at: datetime()
```

---

## 💡 핵심 차이점

| 항목 | Before (JSON) | After (Graph) |
|------|---------------|---------------|
| **저장 방식** | JSON 문자열 | 별도 노드 |
| **검색** | JSON 파싱 필요 | Cypher 쿼리 |
| **중복 처리** | 어려움 | MERGE 자동 처리 |
| **관계 표현** | 불가능 | 관계 노드로 표현 |
| **쿼리 예시** | `WHERE metadata.entities_json CONTAINS 'Elon'` | `MATCH (e:Entity {name: 'Elon Musk'})` |

---

## 🔧 구현 세부사항

### Entity 노드 생성 (MERGE)
```cypher
MERGE (e:Entity {name: $name})
ON CREATE SET 
    e.type = $type,
    e.normalized_name = toLower($name),
    e.created_at = datetime()
RETURN e.name as name
```

**MERGE의 장점:**
- Entity 중복 방지 (같은 이름은 하나만 생성)
- 여러 Document에서 동일 Entity 언급 시 자동으로 기존 노드 재사용

### MENTIONS 관계 생성
```cypher
MATCH (d:Document {id: $doc_id})
MATCH (e:Entity {name: $entity_name})
MERGE (d)-[r:MENTIONS]->(e)
ON CREATE SET r.created_at = datetime()
```

### Unique Constraint
```cypher
CREATE CONSTRAINT entity_name_unique IF NOT EXISTS 
FOR (e:Entity) REQUIRE e.name IS UNIQUE
```

---

## 📈 활용 예시

### 1. Entity로 Document 검색
```cypher
MATCH (d:Document)-[:MENTIONS]->(e:Entity {name: 'Elon Musk'})
RETURN d
```

### 2. Document의 모든 Entity 조회
```cypher
MATCH (d:Document {id: 'doc-123'})-[:MENTIONS]->(e:Entity)
RETURN e.name, e.type
```

### 3. Entity 통계
```cypher
MATCH (e:Entity {name: 'Tesla'})<-[:MENTIONS]-(d:Document)
RETURN e.name, count(d) as mention_count
```

### 4. 전체 Entity 목록 (type별 정렬)
```cypher
MATCH (e:Entity)
RETURN e.name, e.type
ORDER BY e.type, e.name
LIMIT 100
```

---

## 🔮 향후 확장 가능성

### Entity 간 관계 (Future Work)
```cypher
# 예시: Elon Musk가 Tesla를 설립
(Elon Musk:Entity)-[:FOUNDED]->(Tesla:Entity)

# 예시: Tesla가 AI 기술 사용
(Tesla:Entity)-[:USES]->(AI:Entity)
```

**이것이 진정한 Knowledge Graph의 핵심!**

---

## 📝 참고

- **Spec 005**: LLM이 Entity 추출 (JSON으로 저장)
- **Spec 007**: EntityType, RelationshipType 스키마 정의
- **Spec 010**: Entity를 Graph 노드로 구축
- **Future Spec**: Entity 간 관계 추출

---

**작성일:** 2026-01-18  
**관련 PR:** [PR #12](https://github.com/Changsik00/rag-ingestion/pull/12)
