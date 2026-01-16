# PR: feat(spec-007): Ontology Design (Multi-layered)

## 📌 Summary

**Spec 007 완료**: Entity 타입 체계 확립 및 Relationship 스키마 정의를 통해 Knowledge Graph 구축을 위한 **데이터 계약(Data Contract)**을 완성했습니다.

### 주요 변경사항

1. **Entity 타입 표준화** (7개):
   - `PERSON`, `ORGANIZATION`, `TECHNOLOGY`, `CONCEPT`, `LOCATION`, `EVENT`, `ACTIVITY` 
   - Python `Enum`으로 정의하여 타입 안정성 확보

2. **Relationship 타입 정의** (8개):
   - Document-Entity: `MENTIONS`
   - Entity-Entity: `WORKS_FOR`, `FOUNDED`, `USES`, `RELATED_TO`, `PERFORMED`, `SUPPORTS`, `PART_OF`

3. **Breaking Change**: 
   - `ExtractedMetadata.entities`: `Dict[str, List[str]]` → `Dict[EntityType, List[str]]`

4. **LLM Prompt 강화**:
   - Entity 분류 규칙 명시
   - 각 타입별 예시 및 가이드라인 추가

---

## 🔍 Key Review Points

### 1. Domain Layer - Type Safety 확보

**변경 파일**: [`app/domain/schemas/ontology.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/ontology.py)

- `EntityType`, `RelationshipType`: str 기반 Enum으로 JSON 직렬화 용이
- `TypedEntity`: 향후 확장 지원 (신뢰도 등 메타데이터 추가 가능)

**설계 결정**:
- ✅ `Enum` 사용 → LLM이 임의 타입 생성 방지
- ✅ `str` 기반 → JSON 호환성
- ✅ 프레임워크 독립적 → Clean Architecture 준수

---

### 2. Breaking Change - 안전한 마이그레이션

**변경 파일**: [`app/domain/schemas/extraction.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/extraction.py)

**Before**:
```python
entities: Dict[str, List[str]] = {
    "Person": ["Elon Musk"],  # ❌ 자유 형식
    "Technology": ["Python"]
}
```

**After**:
```python
entities: Dict[EntityType, List[str]] = {
    EntityType.PERSON: ["Elon Musk"],     # ✅ 타입 안전
    EntityType.TECHNOLOGY: ["Python"]
}
```

**영향 범위**:
- 기존 저장된 데이터는 영향 없음 (새 데이터만 적용)
- 모든 테스트 업데이트 완료

---

### 3. LLM 정확도 향상 - 상세한 분류 규칙

**변경 파일**: [`app/infrastructure/llm/langchain_adapter.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/llm/langchain_adapter.py)

**개선사항**:
- 7개 Entity 타입 각각에 대한 설명 및 예시 추가
- `ACTIVITY` 타입 지원 (한글 활동명 포함: "책 쓰기", "벤치마킹")
- Fallback 지시: 애매한 경우 `CONCEPT` 사용

**검증 결과** (Manual Verification):
```
Entities: {
  <EntityType.TECHNOLOGY: 'TECHNOLOGY'>: ['LangChain'],
  <EntityType.CONCEPT: 'CONCEPT'>: ['Language Models'],
  <EntityType.ORGANIZATION: 'ORGANIZATION'>: ['SpaceX'],
  <EntityType.PERSON: 'PERSON'>: ['Elon Musk'],
  <EntityType.LOCATION: 'LOCATION'>: ['Hawthorne', 'California'],
  <EntityType.ACTIVITY: 'ACTIVITY'>: ['Colonization']
}
```
✅ LLM이 정확히 `EntityType` Enum 사용 확인

---

## ✅ Verification Plan

### Automated Tests

#### 1. Unit Tests (**13/13 PASSED** ✅)

**New**: [`tests/unit/domain/test_ontology.py`](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/domain/test_ontology.py)
- Entity 타입 7개 검증
- Relationship 타입 8개 검증
- 다양한 Entity 목 데이터 (Person, Organization, Technology, Concept, Location, Event, Activity)
- 한글 활동명 처리 ("책 쓰기", "벤치마킹", "코드 리뷰")

**Updated**: [`tests/unit/domain/test_extractor.py`](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/domain/test_extractor.py)
- Mock 데이터를 `EntityType` Enum 사용으로 변경
- 다양한 Entity 타입 테스트

**실행 명령어**:
```bash
uv run pytest tests/unit/domain/ -v
```

---

#### 2. Integration Tests (**5/5 PASSED** ✅)

**확인 사항**:
- API 엔드포인트 정상 작동
- Job 상태 관리 정상 작동

**실행 명령어**:
```bash
uv run pytest tests/integration/ -v
```

---

### Manual Verification

#### 1. LLM Extraction 품질 확인 ✅

**실행 방법**:
```bash
uv run python scripts/manual_verify_extraction.py
```

**검증 완료**:
- [x] Entity 키가 모두 `EntityType` Enum 값
- [x] 분류 품질 적절 (예: "SpaceX" → ORGANIZATION, "Elon Musk" → PERSON)

---

#### 2. API Response 검증 (Optional)

API가 실행 중이라면 다음 명령어로 확인 가능:

```bash
curl -X POST "http://localhost:8000/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/tech-article"}'
```

**확인 사항**:
- `entities` 필드 구조가 올바른지 확인 (Enum 키)
- Swagger UI (`http://localhost:8000/docs`)에서 스키마 변경 확인

---

## 📚 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Schema Definition | Pydantic `BaseModel` + `Enum` | 타입 안정성 및 직렬화 |
| LLM Integration | LangChain (LCEL) | Prompt 템플릿 관리 |
| Testing | pytest | Unit/Integration 테스트 |
| Documentation | Markdown | 설계 근거 문서화 ([`docs/ontology.md`](file:///Users/ck/Project/doit/rag-ingestion/docs/ontology.md)) |

---

## 📝 Files Changed

### Domain Layer
- 🆕 [`app/domain/schemas/ontology.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/ontology.py) - Entity & Relationship 타입 정의
- ✏️ [`app/domain/schemas/extraction.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/extraction.py) - `ExtractedMetadata` 타입 변경

### Infrastructure Layer
- ✏️ [`app/infrastructure/llm/langchain_adapter.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/llm/langchain_adapter.py) - LLM Prompt 강화

### Tests
- 🆕 [`tests/unit/domain/test_ontology.py`](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/domain/test_ontology.py) - Ontology 스키마 테스트
- ✏️ [`tests/unit/domain/test_extractor.py`](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/domain/test_extractor.py) - Mock 데이터 업데이트

### Documentation
- 🆕 [`docs/ontology.md`](file:///Users/ck/Project/doit/rag-ingestion/docs/ontology.md) - Ontology 설계 문서 (ADR 포함)

---

## 🚀 Next Steps (Spec 008)

현재 Spec은 **"설계도 작성"** 단계입니다. 다음 Spec에서 실제 구현 예정:

1. **Entity-Entity 관계 추출**
   - LLM이 "Elon Musk founded Tesla" → `(:Person)-[:FOUNDED]->(:Organization)` 추출

2. **Neo4j에 노드/관계 생성**
   - Infrastructure 레이어에서 Neo4j Driver 활용
   - `CREATE` 쿼리 자동 생성

3. **Graph 탐색 API 개발**
   - `GET /graph/entity/{entity_name}` 엔드포인트 추가

---

## 🎯 Commit History

```
a93c5d3 feat(domain): add ontology schema with entity and relationship types
6400fcd refactor(domain): update ExtractedMetadata to use EntityType enum
024f9d6 test(domain): update extractor tests for typed entities
3211fdd feat(infrastructure): add entity type constraints to LLM prompt
36fed2d docs: add ontology design documentation
```

---

**관련 문서**:
- 📄 [Spec 007](file:///Users/ck/Project/doit/rag-ingestion/specs/007-ontology-design/spec.md)
- 📋 [Plan 007](file:///Users/ck/Project/doit/rag-ingestion/specs/007-ontology-design/plan.md)
- ✅ [Task 007](file:///Users/ck/Project/doit/rag-ingestion/specs/007-ontology-design/task.md)
