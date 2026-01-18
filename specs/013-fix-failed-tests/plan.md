# Implementation Plan: Spec 013 - Fix Failed Tests

## 📋 Summary

Spec 006, 010, 011 이후 발생한 **6개의 테스트 실패**를 수정하여 전체 테스트 스위트를 정상화합니다.

**주요 변경점:**
1. DI 테스트 Import 경로 수정 (`app.core.dependencies` → `app.interfaces.api.dependencies`)
2. Use Case 테스트 Mock 설정 업데이트 (`graph`, `extractor` 파라미터 추가)

**⚠️ 중요:**
- 프로덕션 코드는 **절대 변경하지 않음**
- 테스트 코드만 최소한으로 수정

---

## 🌳 Branch Strategy

```bash
# 브랜치 생성
git checkout -b feature/013-fix-failed-tests

# PR 제목
test(spec-013): fix failed tests after refactoring
```

---

## 🔍 Root Cause Analysis

### 문제 1: DI 테스트 Import 경로 불일치

**영향받은 파일:** `tests/integration/tdd/test_dependency_injection.py`  
**실패 테스트:** 3개 (`test_get_neo4j_storage`, `test_get_chroma_storage`, `test_get_composite_storage`)

**원인 (Spec 011):**
```python
# 구조 변경 전 (Spec 011 이전)
app/core/dependencies.py  # ❌ 이 파일에서 DI 함수들 정의

# 구조 변경 후 (Spec 011 이후)
app/interfaces/api/dependencies.py  # ✅ 여기로 이동
```

**추가 조사 필요:**
- `get_neo4j_storage()`, `get_chroma_storage()`, `get_composite_storage()` 함수가 실제로 존재하는가?
- 현재 `dependencies.py`에는 `get_repository()`만 있을 가능성
- 존재하지 않으면 테스트 재작성 또는 삭제 필요

---

### 문제 2: IngestionService 생성자 시그니처 변경

**영향받은 파일:** `tests/unit/test_usecases.py`  
**실패 테스트:** 3개 (`test_create_job`, `test_process_job_success`, `test_process_job_failure`)

**원인 (Spec 010):**
```python
# Before (Spec 010 이전)
class IngestionService:
    def __init__(
        self,
        scraper: ScraperInterface,
        repository: DocumentRepository,
        job_repository: JobRepository
    ):
        ...

# After (Spec 010 이후)
class IngestionService:
    def __init__(
        self,
        scraper: ScraperInterface,
        repository: DocumentRepository,
        graph: GraphRepository,  # ✅ 추가 (Knowledge Graph)
        job_repository: JobRepository,
        extractor: SemanticExtractor | None = None  # ✅ 추가 (Optional)
    ):
        ...
```

**필요한 Mock:**
- `mock_graph_repo = Mock()` (GraphRepository)
- `extractor=None` (Optional이므로 None 전달)

---

## 📝 Implementation Approach

### 방식 1: DI 테스트 Import 경로 수정

**Case A - 함수가 존재하는 경우:**
```python
# tests/integration/tdd/test_dependency_injection.py
# Before
from app.core.dependencies import get_neo4j_storage

# After
from app.interfaces.api.dependencies import get_neo4j_storage
```

**Case B - 함수가 없는 경우 (테스트 재작성):**
```python
# tests/integration/tdd/test_dependency_injection.py
from app.interfaces.api.dependencies import get_repository
from app.infrastructure.storage.composite import CompositeStorage

def test_get_repository_returns_composite_storage():
    """
    Verify that get_repository() creates CompositeStorage with Neo4j and Chroma
    """
    # When: DI container provides repository
    repository = get_repository()
    
    # Then: Instance is CompositeStorage
    assert repository is not None
    assert isinstance(repository, CompositeStorage)
    assert len(repository.storages) == 2  # Neo4j + Chroma
```

---

### 방식 2: Use Case 테스트 생성자 파라미터 추가

**수정 패턴 (3개 테스트 공통):**
```python
# Before
def test_create_job():
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_job_repo = Mock()
    service = IngestionService(
        scraper=mock_scraper,
        repository=mock_doc_repo,
        job_repository=mock_job_repo
    )

# After
def test_create_job():
    mock_scraper = Mock(spec=ScraperInterface)
    mock_doc_repo = Mock()
    mock_graph_repo = Mock()  # ✅ GraphRepository Mock 추가
    mock_job_repo = Mock()
    service = IngestionService(
        scraper=mock_scraper,
        repository=mock_doc_repo,
        graph=mock_graph_repo,  # ✅ 추가
        job_repository=mock_job_repo,
        extractor=None  # ✅ Optional이므로 None
    )
```

**적용 대상:**
1. `test_create_job` (Line 9-22)
2. `test_process_job_success` (Line 24-53)
3. `test_process_job_failure` (Line 55-80)

---

## ✅ Verification Plan

### 1. Individual Test Files

```bash
# DI 테스트 (3개)
pytest tests/integration/tdd/test_dependency_injection.py -v
# 예상: 3 passed

# Use Case 테스트 (3개)
pytest tests/unit/test_usecases.py -v
# 예상: 3 passed
```

### 2. Full Test Suite (회귀 방지)

```bash
# 전체 테스트 실행
pytest tests/ -v

# Contract Tests
pytest tests/contracts/ -v

# Integration Tests
pytest tests/integration/ -v
```

### 3. CI Pipeline

```bash
# PR 생성 전 로컬 검증
pytest tests/ --cov=app --cov-report=term-missing
```

---

## 📦 File Changes Summary

### 수정 파일
- `tests/integration/tdd/test_dependency_injection.py` - Import 경로 수정 또는 테스트 재작성
- `tests/unit/test_usecases.py` - Mock 설정 업데이트 (3개 테스트)

### 신규/삭제 파일
- 없음

---

## ⚠️ Breaking Changes

**없음** - 테스트 코드만 수정하므로 프로덕션에 영향 없음

---

## 🎯 Success Criteria

1. ✅ 6개 실패 테스트 모두 통과
2. ✅ 전체 테스트 스위트 통과 (회귀 없음)
3. ✅ CI 파이프라인 통과
4. ✅ 프로덕션 코드 변경 없음
