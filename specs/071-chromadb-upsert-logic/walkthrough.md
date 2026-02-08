# Walkthrough: Spec 071 - ChromaDB Upsert Logic

> **작성일**: 2026-02-08  
> **Mode**: EXECUTION  
> **Status**: ✅ 완료

---

## 📋 작업 개요

**목표**: ChromaDB의 중복 저장 방지를 위해 `add` 메서드를 `upsert`로 변경

**근거**: [Spec 068 - Root Cause #1](../068-rag-architecture-review/root_cause_analysis.md#-critical-issue-1-ingestion-data-consistency-좀비-데이터)

**Expected Impact**:
- 중복 저장률: 100% → 0%
- 동일 문서 재수집 시 안정적 동작
- Neo4j와 ChromaDB 데이터 일관성 보장

---

## ✅ 완료된 작업

### Task 1: 브랜치 생성 및 환경 확인
- [x] Feature 브랜치 생성: `feature/071-chromadb-upsert-logic`
- [x] ChromaDB 1.4.1 버전 확인
- [x] `upsert` 메서드 지원 확인 (Web Search로 Documentation 확인)
- [x] 기존 Unit Test 통과 확인

### Task 2: Integration Test 작성 (TDD)
- [x] `tests/integration/test_duplicate_ingestion.py` 작성
- [x] 3가지 테스트 케이스 구현:
  - `test_duplicate_document_upsert`: Document 중복 수집 테스트
  - `test_duplicate_chunks_upsert`: Chunk 중복 수집 테스트
  - `test_batch_chunks_upsert`: 배치 청크 중복 수집 테스트
- [x] TDD 방식으로 테스트 Fail 확인

### Task 3: ChromaDB Repository 수정
- [x] `app/infrastructure/repositories/chroma.py` 수정:
  - Line 102: `save()` 메서드 `add` → `upsert` 변경
  - Line 152: `save_chunks()` 메서드 `add` → `upsert` 변경
- [x] Unit Test `tests/unit/infrastructure/repositories/test_chroma.py` 수정:
  - Mock 검증 `add` → `upsert` 변경
- [x] Integration Test 통과 확인

### Task 4: Code Quality & Testing
- [x] Ruff 검사 및 포맷 실행
- [x] Test Fixture 개선 (테스트 전 컬렉션 리셋 추가)
- [x] 모든 관련 테스트 통과 (4 passed)

---

## 🔍 핵심 변경 사항

### Before: `add` 메서드 (중복 시 에러)
```python
# app/infrastructure/repositories/chroma.py
self.collection.add(
    documents=[document.content], 
    metadatas=[flattened_metadata], 
    ids=[str(document.id)]
)
```

**문제점**:
- 동일 ID로 재호출 시 ERROR 발생
- 동일 문서 재수집 시 Ingestion 실패

### After: `upsert` 메서드 (멱등성 보장)
```python
# app/infrastructure/repositories/chroma.py
self.collection.upsert(
    documents=[document.content], 
    metadatas=[flattened_metadata], 
    ids=[str(document.id)]
)
```

**개선 효과**:
- ID 존재 시 → UPDATE (기존 데이터 업데이트)
- ID 없을 시 → INSERT (신규 데이터 생성)
- 멱등성 보장: 동일 문서 여러 번 수집해도 안전

---

## 🧪 검증 결과

### Automated Tests

**Integration Test 결과**: ✅ 3 passed
```bash
$ uv run pytest tests/integration/test_duplicate_ingestion.py -v

tests/integration/test_duplicate_ingestion.py::test_duplicate_document_upsert PASSED
tests/integration/test_duplicate_ingestion.py::test_duplicate_chunks_upsert PASSED  
tests/integration/test_duplicate_ingestion.py::test_batch_chunks_upsert PASSED
```

**Unit Test 결과**: ✅ 1 passed
```bash
$ uv run pytest tests/unit/infrastructure/repositories/test_chroma.py -v

tests/unit/infrastructure/repositories/test_chroma.py::test_chroma_storage_save_chunks PASSED
```

### Test Coverage

| Test Case | Purpose | Result |
|-----------|---------|--------|
| `test_duplicate_document_upsert` | Document 중복 수집 시 업데이트만 발생 | ✅ PASS |
| `test_duplicate_chunks_upsert` | Chunk 중복 수집 시 업데이트만 발생 | ✅ PASS |
| `test_batch_chunks_upsert` | 배치 청크 중복 방지 (10개 → 10개 유지) | ✅ PASS |

---

## 📝 Neo4j vs ChromaDB 비교

### Neo4j: 이미 Upsert 방식 ✅
```cypher
MERGE (d:Document {id: $id})  -- ID 존재 시 UPDATE, 없으면 INSERT
SET d.content = $content
```

### ChromaDB: 이제 Upsert 방식 적용 ✅
```python
collection.upsert(...)  -- Neo4j와 동일한 멱등성 보장
```

**결과**: Neo4j와 ChromaDB 모두 동일한 중복 처리 로직 사용 → 데이터 일관성 보장

---

## 🚀 다음 단계

**Spec 072: Robust Deduplication Framework**로 확장 예정:
- 4가지 Deduplication Strategy (ID/Metadata/TTL/Contents)
- Admin UI에서 Strategy 선택 기능
- ChromaDB `upsert` 로직이 Deduplication의 기반이 됨

---

## 📦 Commits

1. `chore(spec-071): create feature branch for chromadb upsert logic`
2. `test(spec-071): add integration test for duplicate ingestion`
3. `feat(spec-071): replace chromadb add with upsert for duplicate prevention`
4. `test(spec-071): fix test fixture to reset collection before each test`

**Total**: 4 commits, 3 files changed
