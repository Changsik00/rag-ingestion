# Task: Spec 007 - Ontology Design (Multi-layered)

## 📋 Planning Phase

- [x] 현재 코드베이스 분석 (Entity 구조 파악)
- [x] Spec 문서 작성 (`spec.md`)
- [x] Plan 문서 작성 (`plan.md`)
- [x] Task 체크리스트 작성 (`task.md`)
- [x] 사용자 리뷰 및 Plan Accept 대기

---

## 🚀 Execution Phase (Plan Accept 후 진행)

### Task 1: Feature 브랜치 생성
- [x] main 브랜치에서 `feature/007-ontology-design` 브랜치 생성
- [x] 브랜치 전환 확인 (`git branch --show-current`)

### Task 2: Domain - Ontology Schema 정의
- [x] `app/domain/schemas/ontology.py` 생성
  - [x] `EntityType` Enum 정의 (7개 타입: PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, LOCATION, EVENT, ACTIVITY)
  - [x] `RelationshipType` Enum 정의 (8개 관계: MENTIONS, WORKS_FOR, FOUNDED, USES, RELATED_TO, PERFORMED, SUPPORTS, PART_OF)
  - [x] `TypedEntity` Model 정의 (향후 확장용)
- [x] 테스트 작성: `tests/unit/domain/test_ontology.py`
  - [x] `test_entity_type_enum_values()`
  - [x] `test_relationship_type_enum()`
  - [x] `test_extracted_metadata_with_typed_entities()`
- [x] 테스트 실행 및 통과 확인: `pytest tests/unit/domain/test_ontology.py -v`
- [x] 커밋: `feat(domain): add ontology schema with entity and relationship types`

### Task 3: Domain - ExtractedMetadata 스키마 업데이트
- [x] `app/domain/schemas/extraction.py` 수정
  - [x] `entities` 필드 타입 변경: `Dict[str, List[str]]` → `Dict[EntityType, List[str]]`
  - [x] import 추가: `from app.domain.schemas.ontology import EntityType`
  - [x] example 업데이트 (Enum 키 사용)
- [x] 테스트 실행 확인: `pytest tests/unit/domain/ -v` (기존 테스트 깨지는지 확인)
- [x] 커밋: `refactor(domain): update ExtractedMetadata to use EntityType enum`

### Task 4: Tests - 기존 테스트 업데이트
- [x] `tests/unit/domain/test_extractor.py` 수정
  - [x] Mock 데이터의 `entities` 필드를 `EntityType` 사용하도록 변경
  - [x] import 추가: `from app.domain.schemas.ontology import EntityType`
- [x] 테스트 실행 및 통과 확인: `pytest tests/unit/domain/test_extractor.py -v`
- [x] 커밋: `test(domain): update extractor tests for typed entities`

### Task 5: Infrastructure - LangChain Prompt 업데이트
- [x] `app/infrastructure/llm/langchain_adapter.py` 수정
  - [x] Prompt 템플릿에 Entity 타입 제약 명시
  - [x] 각 타입별 설명 및 예시 추가
- [x] 수동 검증 스크립트 실행: `uv run python scripts/manual_verify_extraction.py`
  - [x] Entity 키가 모두 Enum 값인지 확인
  - [x] 분류 품질 육안 확인
- [x] 커밋: `feat(infrastructure): add entity type constraints to LLM prompt`

### Task 6: Documentation - Ontology 설계 문서 작성
- [x] `docs/ontology.md` 생성
  - [x] Entity 타입 정의 및 선택 근거
  - [x] Relationship 타입 정의 및 활용 시나리오
  - [x] 설계 결정 기록 (ADR)
  - [x] 향후 계획 (Spec 008 연계)
- [x] 커밋: `docs: add ontology design documentation`

### Task 7: 통합 테스트 및 검증
- [x] 전체 테스트 실행: `pytest -v`
- [x] API 수동 테스트:
  - [x] POST `/ingest/web` 호출하여 응답 확인
  - [x] Swagger UI (`/docs`)에서 스키마 확인
- [x] Ruff Linter 실행: `uv run ruff check .`
- [x] 필요 시 수정 후 커밋: `fix: resolve linting issues`

### Task 8: PR 준비 및 생성
- [x] `specs/007-ontology-design/pr_description.md` 작성
  - [x] Summary (변경 개요)
  - [x] Key Review Points (리뷰 포인트)
  - [x] Verification Plan (검증 방법)
  - [x] Tech Stack
- [x] 전체 테스트 재실행 확인: `pytest -v`
- [x] GitHub PR 생성: `gh pr create -F specs/007-ontology-design/pr_description.md`
- [x] PR URL 사용자에게 보고
