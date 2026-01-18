# Implementation Plan: Spec 014 - Code Quality Improvement

## 📋 Summary

코드 품질 개선을 위한 두 가지 작업:
1. `semantic_data` undefined 버그 수정
2. TDD 테스트 GWT 형식 통일 (9개 파일)

**주요 변경점:**
1. `app/use_cases/ingestion.py` 버그 수정
2. Unit/TDD Integration 테스트 9개 파일 GWT 주석 추가

**⚠️ 중요:**
- 프로덕션 코드는 버그 수정만 (1줄 추가)
- 테스트 코드는 주석만 추가 (로직 변경 없음)

---

## 🌳 Branch Strategy

```bash
# 브랜치 생성
git checkout -b feature/014-code-quality-improvement

# PR 제목
fix(spec-014): code quality improvements (bug fix + test standardization)
```

---

## 🔍 Root Cause Analysis

### 문제 1: semantic_data NameError

**발생 조건:**
- `IngestionService(extractor=None)` 생성
- `process_job()` 실행 시 Line 74에서 `NameError: name 'semantic_data' is not defined`

**원인:**
```python
# Line 52-61
if self.extractor:  # extractor=None이면 이 블록 실행 안 됨
    try:
        semantic_data = self.extractor.extract(...)  # semantic_data 정의
    except Exception as e:
        print(...)

# Line 74
if semantic_data and semantic_data.entities:  # ❌ 정의되지 않음
    self._build_knowledge_graph(...)
```

---

### 문제 2: GWT 형식 불일치

**일관성 부족:**
- BDD: 100% GWT 적용
- TDD DI: 100% GWT 적용
- Unit: 0% GWT 적용 ❌
- TDD Integration: 일부만 적용

---

## 📝 Implementation Approach

### 방식 1: Bug Fix

**파일:** `app/use_cases/ingestion.py`

**변경 내용:**
```python
# Before (Line 51-75)
# 3. Semantic Extraction (Spec 005)
if self.extractor:
    try:
        semantic_data = self.extractor.extract(result.markdown)
        if semantic_data:
            result.metadata["semantic_data"] = semantic_data.model_dump()
    except Exception as e:
        print(f"Semantic extraction failed for job {job_id}: {e}")

# ... (Line 64-72: Document 생성 및 저장)

# 6. Build Knowledge Graph (Spec 010)
if semantic_data and semantic_data.entities:  # ❌ NameError
    self._build_knowledge_graph(doc.id, semantic_data.entities)

# After
semantic_data = None  # ✅ 초기화

# 3. Semantic Extraction (Spec 005)
if self.extractor:
    try:
        semantic_data = self.extractor.extract(result.markdown)
        if semantic_data:
            result.metadata["semantic_data"] = semantic_data.model_dump()
    except Exception as e:
        print(f"Semantic extraction failed for job {job_id}: {e}")

# ... (Line 64-72: Document 생성 및 저장)

# 6. Build Knowledge Graph (Spec 010)
if semantic_data and semantic_data.entities:  # ✅ None check 가능
    self._build_knowledge_graph(doc.id, semantic_data.entities)
```

---

### 방식 2: GWT 표준화

**표준 템플릿:**
```python
def test_example():
    # Given: [테스트 조건 설명]
    setup_code()
    
    # When: [테스트할 동작]
    result = target_function()
    
    # Then: [기대 결과]
    assert result == expected
```

**적용 대상 (9개 파일):**

#### Unit Tests (6개)
1. `test_job_entity.py` (2 tests)
2. `test_neo4j_graph_repository.py` (7 tests)
3. `test_neo4j_job_repo.py` (4 tests)
4. `test_scraper.py` (2 tests)
5. `test_storage.py` (2 tests)
6. `test_usecases.py` (3 tests)

#### TDD Integration Tests (3개)
7. `test_api_ingest.py` (2 tests)
8. `test_async_ingest.py` (2 tests)
9. `test_jobs.py` (4 tests)

**예시 (test_usecases.py):**
```python
# Before
def test_create_job():
    # Arrange
    mock_scraper = Mock(spec=ScraperInterface)
    # ...
    
    # Act
    job = service.create_job("http://example.com")
    
    # Assert
    assert job.source_url == "http://example.com"

# After
def test_create_job():
    # Given: IngestionService with mocked dependencies
    mock_scraper = Mock(spec=ScraperInterface)
    # ...
    
    # When: Job 생성 요청
    job = service.create_job("http://example.com")
    
    # Then: Job이 PENDING 상태로 생성됨
    assert job.source_url == "http://example.com"
    assert job.status == JobStatus.PENDING
```

---

## ✅ Verification Plan

### 1. Bug Fix 검증

```bash
# Unit 테스트 실행
uv run pytest tests/unit/test_usecases.py::test_process_job_success -v

# extractor=None 케이스 확인
uv run pytest tests/unit/test_usecases.py -v
```

### 2. GWT 표준화 검증

```bash
# 각 파일별 확인
uv run pytest tests/unit/ -v
uv run pytest tests/integration/tdd/ -v

# 전체 테스트 (회귀 방지)
uv run pytest tests/ -v
```

---

## 📦 File Changes Summary

### 수정 파일
**Production:**
- `app/use_cases/ingestion.py` (+1 line)

**Tests:**
- `tests/unit/test_job_entity.py`
- `tests/unit/test_neo4j_graph_repository.py`
- `tests/unit/test_neo4j_job_repo.py`
- `tests/unit/test_scraper.py`
- `tests/unit/test_storage.py`
- `tests/unit/test_usecases.py`
- `tests/integration/tdd/test_api_ingest.py`
- `tests/integration/tdd/test_async_ingest.py`
- `tests/integration/tdd/test_jobs.py`

### 신규/삭제 파일
- 없음

---

## ⚠️ Breaking Changes

**없음** - 버그 수정 및 주석 추가만 수행

---

## 🎯 Success Criteria

1. ✅ `semantic_data` 버그 수정
2. ✅ 9개 파일 GWT 형식 통일
3. ✅ 전체 테스트 스위트 통과 (85+ passed)
4. ✅ 회귀 없음
