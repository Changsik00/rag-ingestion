# Walkthrough: Spec 013 - Fix Failed Tests

## 📋 Summary

Spec 006, 010, 011 이후 발생한 **6개의 테스트 실패**를 모두 수정했습니다.

**수정 결과:**
- ✅ DI 테스트: 3 passed, 1 skipped
- ✅ Use Case 테스트: 3 passed  
- ✅ 전체 테스트 스위트: **85 passed, 4 skipped** (회귀 없음)

---

## 🔧 Changes Made

### 1. DI 테스트 수정 ([test_dependency_injection.py](file:///Users/ck/Project/doit/rag-ingestion/tests/integration/tdd/test_dependency_injection.py))

**문제:**
- `app.core.dependencies` 모듈이 존재하지 않음 (Spec 011에서 제거됨)
- `get_neo4j_storage()`, `get_chroma_storage()`, `get_composite_storage()` 함수 없음

**해결:**
- Import 경로 변경: `app.core.dependencies` → `app.interfaces.api.dependencies`
- 3개 테스트 재작성:
  1. `test_get_neo4j_storage` → `test_get_repository_returns_composite_storage`
  2. `test_get_chroma_storage` → `test_get_neo4j_driver_initialization`
  3. `test_get_composite_storage` → `test_get_graph_repository`

**핵심 변경:**
```python
# Before
from app.core.dependencies import get_neo4j_storage

# After
from app.interfaces.api.dependencies import get_repository, get_neo4j_driver

driver = get_neo4j_driver()
repository = get_repository(driver)
```

---

### 2. Use Case 테스트 수정 ([test_usecases.py](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/test_usecases.py))

**문제:**
- `IngestionService` 생성자가 Spec 010 이후 변경됨
- `graph: GraphRepository`, `extractor: SemanticExtractor` 파라미터 추가됨

**해결:**
- 3개 모든 테스트에 Mock 추가:
  - `mock_graph_repo = Mock()`
  - `mock_extractor = Mock()` 또는 `extractor=None`

**핵심 변경:**
```python
# Before (Line 14)
service = IngestionService(
    scraper=mock_scraper,
    repository=mock_doc_repo,
    job_repository=mock_job_repo
)

# After
service = IngestionService(
    scraper=mock_scraper,
    repository=mock_doc_repo,
    graph=mock_graph_repo,      # ✅ 추가
    job_repository=mock_job_repo,
    extractor=None               # ✅ 추가
)
```

---

## 🧪 Test Results

### DI Tests (Before)
```
FAILED test_get_neo4j_storage - ModuleNotFoundError: No module named 'app.core.dependencies'
FAILED test_get_chroma_storage - ModuleNotFoundError: No module named 'app.core.dependencies'
FAILED test_get_composite_storage - ModuleNotFoundError: No module named 'app.core.dependencies'
```

### DI Tests (After)
```
✅ test_get_repository_returns_composite_storage PASSED
✅ test_get_neo4j_driver_initialization PASSED
✅ test_get_graph_repository PASSED  
⏭️  test_environment_variable_based_initialization SKIPPED
```

---

### Use Case Tests (Before)
```
FAILED test_create_job - TypeError: missing required positional argument 'graph'
FAILED test_process_job_success - TypeError: missing required positional argument 'graph'  
FAILED test_process_job_failure - TypeError: missing required positional argument 'graph'
```

### Use Case Tests (After)
```
✅ test_create_job PASSED
✅ test_process_job_success PASSED
✅ test_process_job_failure PASSED
```

---

### Full Test Suite
```
============ 85 passed, 4 skipped, 15 warnings in 68.06s =============
```

**회귀 없음 확인:**
- Contract Tests: All passed
- Unit Tests: All passed  
- Integration Tests: All passed
- BDD Tests: All passed

---

## 📊 Files Changed

### Modified Files
- [tests/integration/tdd/test_dependency_injection.py](file:///Users/ck/Project/doit/rag-ingestion/tests/integration/tdd/test_dependency_injection.py)
  - Import 경로 수정 및 테스트 재작성
  - 88 insertions(+), 88 deletions(-)
  
- [tests/unit/test_usecases.py](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/test_usecases.py)
  - Mock 파라미터 추가 (graph, extractor)  
  - 29 insertions(+), 4 deletions(-)

### No Production Code Changes
✅ 프로덕션 코드는 전혀 변경하지 않음 (테스트만 수정)

---

## ✅ Success Criteria

- [x] 6개 실패 테스트 모두 통과
- [x] 전체 테스트 스위트 통과 (85 passed, 4 skipped)
- [x] 회귀 없음 (기존 테스트 전부 통과)
- [x] 프로덕션 코드 변경 없음

---

## 📝 Notes

**DI 테스트 설계 변경:**
- 기존: 개별 storage getter 함수 테스트
- 현재: 실제 DI 구조를 반영한 통합 테스트 (`get_repository`, `get_neo4j_driver`, `get_graph_repository`)

**Use Case 테스트 Mock 전략:**
- `extractor=None` 사용 시 `semantic_data` 미정의 문제 발생
- `mock_extractor.extract.return_value = None`으로 해결
