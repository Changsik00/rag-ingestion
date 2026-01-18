# ✅ Spec 013: Fix Failed Tests

## 📋 Summary

Spec 006, 010, 011 리팩토링 이후 발생한 **6개의 테스트 실패**를 모두 수정했습니다.

**테스트 수정 결과:**
- ✅ DI 테스트: 3개 수정 (3 passed, 1 skipped)
- ✅ Use Case 테스트: 3개 수정 (3 passed)
- ✅ 전체 테스트 스위트: **85 passed, 4 skipped** ← 회귀 없음

---

## 🔍 Root Cause

### 문제 1: DI 테스트 Import 경로 불일치
- **원인 (Spec 011):** `app.core.dependencies` → `app.interfaces.api.dependencies`로 이동
- **영향:** `ModuleNotFoundError` 발생 (3개 테스트)

### 문제 2: IngestionService 생성자 변경
- **원인 (Spec 010):** Knowledge Graph 구축을 위해 `graph`, `extractor` 파라미터 추가
- **영향:** `TypeError: missing required positional argument` (3개 테스트)

---

## 🔧 Changes

### 1. DI 테스트 재작성 ([test_dependency_injection.py](file:///Users/ck/Project/doit/rag-ingestion/tests/integration/tdd/test_dependency_injection.py))

**수정 전략:** Case B 선택 (테스트 재작성)
- `get_neo4j_storage()`, `get_chroma_storage()`, `get_composite_storage()` 함수 없음
- 현재 DI 구조에 맞게 테스트 재작성

```python
# Before
from app.core.dependencies import get_neo4j_storage
storage = get_neo4j_storage()

# After
from app.interfaces.api.dependencies import get_repository, get_neo4j_driver
driver = get_neo4j_driver()
repository = get_repository(driver)
```

**재작성된 테스트:**
1. `test_get_repository_returns_composite_storage` - CompositeStorage 생성 검증
2. `test_get_neo4j_driver_initialization` - Neo4j Driver 생성 검증
3. `test_get_graph_repository` - GraphRepository 생성 검증

---

### 2. Use Case 테스트 Mock 업데이트 ([test_usecases.py](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/test_usecases.py))

**수정 내용:** 3개 테스트 모두 `graph`, `extractor` Mock 추가

```python
# Before
service = IngestionService(
    scraper=mock_scraper,
    repository=mock_doc_repo,
    job_repository=mock_job_repo
)

# After
service = IngestionService(
    scraper=mock_scraper,
    repository=mock_doc_repo,
    graph=mock_graph_repo,      # ✅ GraphRepository Mock
    job_repository=mock_job_repo,
    extractor=mock_extractor     # ✅ SemanticExtractor Mock
)
```

**수정된 테스트:**
- `test_create_job`
- `test_process_job_success`
- `test_process_job_failure`

---

## 🧪 Verification Plan

### Automated Tests

```bash
# DI 테스트
uv run pytest tests/integration/tdd/test_dependency_injection.py -v
# ✅ 3 passed, 1 skipped

# Use Case 테스트
uv run pytest tests/unit/test_usecases.py -v
# ✅ 3 passed

# 전체 테스트 (회귀 방지)
uv run pytest tests/ -v
# ✅ 85 passed, 4 skipped
```

---

## 📦 Files Changed

**Modified:**
- `tests/integration/tdd/test_dependency_injection.py` (+44, -44)
- `tests/unit/test_usecases.py` (+29, -4)

**No Production Code Changes** ✅

---

## 🎯 Key Review Points

1. **DI 테스트 설계 변경**
   - 기존: 개별 storage getter 테스트 (더 이상 존재하지 않는 함수)
   - 현재: 실제 DI 구조 반영 (`get_repository`, `get_neo4j_driver`, `get_graph_repository`)

2. **Use Case Mock 전략**
   - `extractor=None` 사용 시 프로덕션 코드에서 `NameError` 발생
   - `mock_extractor.extract.return_value = None`으로 해결

3. **회귀 방지 검증**
   - 전체 85개 테스트 모두 통과 확인
   - Contract, Unit, Integration, BDD 테스트 전부 정상

---

## 🚨 Breaking Changes

**없음** - 테스트 코드만 수정, 프로덕션 코드 변경 없음

---

## 📚 Related

- **원인이 된 Spec:**
  - Spec 006: Clean Architecture Refactoring (Protocol 도입)
  - Spec 010: Knowledge Graph Construction (GraphRepository 추가)
  - Spec 011: Infrastructure Refactoring (파일 경로 변경)

- **문서:**
  - [`specs/013-fix-failed-tests/spec.md`](file:///Users/ck/Project/doit/rag-ingestion/specs/013-fix-failed-tests/spec.md)
  - [`specs/013-fix-failed-tests/plan.md`](file:///Users/ck/Project/doit/rag-ingestion/specs/013-fix-failed-tests/plan.md)
  - [`specs/013-fix-failed-tests/walkthrough.md`](file:///Users/ck/Project/doit/rag-ingestion/specs/013-fix-failed-tests/walkthrough.md)

---

## ✅ Definition of Done

- [x] 6개 실패 테스트 모두 수정 완료
- [x] DI 테스트 3개 통과 (3 passed, 1 skipped)
- [x] Use Case 테스트 3개 통과 (3 passed)
- [x] 전체 테스트 스위트 통과 (85 passed, 4 skipped)
- [x] 회귀 없음 (기존 테스트 전부 정상)
- [x] 프로덕션 코드 변경 없음
