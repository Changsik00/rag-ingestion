# PR Description: Spec 010 - Knowledge Graph Construction

## 📋 Summary

Entity를 Neo4j Knowledge Graph로 구축하여 Document-Entity 관계를 시각화하고 쿼리 가능하게 만들었습니다.

**주요 변경점:**
1. `GraphRepository` Protocol 정의 (Domain Layer)
2. Cypher Query Templates 도입 (쿼리 중복 제거)
3. `Neo4jGraphRepository` 구현 (Infrastructure Layer)
4. `IngestionService`에 Entity 그래프 자동 구축
5. Entity 조회 API 엔드포인트 추가
6. 테스트 작성 (Contract, Unit, Integration)

**⚠️ 중요:**
- **LLM 추가 호출 없음** (Spec 005에서 이미 추출된 Entity 사용)
- Entity 간 관계(WORKS_FOR 등)는 향후 별도 Spec에서 구현

---

## 🎯 Problem Statement

**현재 문제:**
- Entity가 JSON 문자열로 Document의 metadata에 직렬화됨
- Entity 간 관계 정보 활용 불가
- Graph 기반 쿼리 불가능 (예: "Elon Musk가 언급된 모든 문서"를 찾을 수 없음)

**해결:**
- Entity를 Neo4j 노드로 생성
- Document-Entity `MENTIONS` 관계 구축
- Entity 기반 Document 검색 API 제공

---

## 🏗️ Architecture Changes

### Before (Spec 005)
```
Document 노드에 metadata.entities_json = '{"PERSON": ["Elon Musk"], ...}'
```

### After (Spec 010)
```cypher
(Document)-[:MENTIONS]->(Entity:PERSON {name: "Elon Musk"})
```

### Graph Schema
```cypher
# Entity 노드
(:Entity {
  name: String,           # 예: "Elon Musk"
  type: String,           # EntityType (PERSON, ORGANIZATION 등)
  normalized_name: String # 검색용 정규화
})

# Document-Entity 관계
(Document)-[:MENTIONS {
  created_at: DateTime
}]->(Entity)
```

---

## 💻 Code Changes

### 신규 파일
- `app/domain/interfaces/graph_repository.py` - GraphRepository Protocol
- `app/infrastructure/storage/cypher_queries.py` - Cypher Query Templates
- `app/infrastructure/storage/neo4j_graph.py` - Neo4jGraphRepository 구현
- `app/interfaces/api/endpoints/entities.py` - Entity API 엔드포인트
- `tests/contracts/test_graph_repository_contract.py` - Contract Tests
- `tests/unit/test_neo4j_graph_repository.py` - Unit Tests
- `tests/integration/bdd/test_knowledge_graph.py` - Integration Tests

### 수정 파일
- `app/use_cases/ingestion.py` - GraphRepository 주입 및 `_build_knowledge_graph` 메서드 추가
- `app/interfaces/api/dependencies.py` - GraphRepository DI 설정
- `app/interfaces/api/main.py` - entities router 추가

---

## 📊 Test Results

### Contract Tests
```
6 passed in 0.31s
- GraphRepository Protocol 검증
- Neo4jGraphRepository 계약 준수 확인
- 메서드 시그니처 검증
```

### Unit Tests
```
7 passed in 0.26s
- save_entity (생성/MERGE)
- create_mention_relationship
- get_entities_by_document
- get_document_ids_by_entity
- list_all_entities
```

### Integration Tests (BDD)
```
3 시나리오 작성 (Docker 환경 필요)
- Entity 그래프 자동 구축
- Entity 기반 Document 검색
- Entity 중복 처리 (MERGE 검증)
```

**전체 결과: 45 passed, 2 skipped** ✅

---

## 🔌 API Changes

### 신규 엔드포인트

**1. GET /entities**
```bash
# 전체 Entity 목록 조회 (type별 정렬)
curl "http://localhost:8000/entities?limit=100"

# Response
[
  {"name": "Elon Musk", "type": "PERSON", "confidence": 1.0},
  {"name": "Tesla", "type": "TECHNOLOGY", "confidence": 1.0}
]
```

**2. GET /entities/{name}/documents**
```bash
# 특정 Entity가 언급된 Document 목록
curl "http://localhost:8000/entities/Elon Musk/documents"

# Response: AtomicDocument[] (해당 Entity가 언급된 모든 문서)
```

**3. GET /entities/{name}/info**
```bash
# Entity 통계 정보
curl "http://localhost:8000/entities/Elon Musk/info"

# Response
{
  "name": "Elon Musk",
  "mention_count": 5,
  "document_ids": ["uuid1", "uuid2", ...]
}
```

---

## 🚀 Usage Example

```bash
# 1. Document 수집 (Entity 자동 추출 및 Graph 구축)
curl -X POST "http://localhost:8000/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://techcrunch.com/article/...", "enable_extraction": true}'

# 2. Entity 목록 확인
curl "http://localhost:8000/entities"

# 3. 특정 Entity로 Document 검색
curl "http://localhost:8000/entities/OpenAI/documents"
```

---

## ⚠️ Breaking Changes

**없음** - 기존 기능에 영향 없이 추가만 수행

---

## 🔮 Future Work

### Phase 1: Entity Relationship Extraction (최우선)
- LLM 프롬프트 개선하여 Entity 간 관계 추출
- 예: "Elon Musk founded Tesla" → `(Elon Musk)-[:FOUNDED]->(Tesla)`
- **이것이 진정한 Knowledge Graph의 핵심**

### Phase 2: Entity Enrichment
- Entity 중복 제거 (Deduplication)
- 외부 KB 연동 (Wikipedia API)
- Entity 별칭 관리

### Phase 3: Advanced Querying
- Cypher 기반 복잡한 그래프 탐색
- Knowledge Path 분석

---

## 📝 Notes

- Integration Tests는 Docker Compose 환경에서 실행 필요
- Entity 중복은 현재 name을 unique key로 처리 (향후 개선)
- Entity 간 관계는 별도 Spec에서 구현 예정

---

## 🙏 Acknowledgments

- Spec 007에서 정의한 `EntityType`, `RelationshipType` 스키마 활용
- Spec 009 Testing Strategy에 따라 Contract, Unit, Integration Tests 작성
