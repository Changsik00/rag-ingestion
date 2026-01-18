# Spec 013: Fix Failed Tests

## 📋 요약

Spec 006, 010, 011 이후 발생한 **6개의 테스트 실패**를 수정하여, 전체 테스트 스위트가 정상적으로 통과하도록 복구합니다.

## 🎯 Background

### 문제 발견
- **발견 시점**: Spec 012 (Integration Test High Priority) 테스트 실행 중
- **실패 개수**: 총 6개
  - `test_dependency_injection.py`: 3개
  - `test_usecases.py`: 3개

### 발생 원인
1. **Spec 006 (Clean Architecture Refactoring)**: Protocol 기반 인터페이스 도입
2. **Spec 010 (Knowledge Graph Construction)**: `IngestionService`에 `GraphRepository` 추가
3. **Spec 011 (Infrastructure Refactoring)**: Import 경로 및 파일명 변경

## 🔍 분석

### 실패 테스트 1: `test_dependency_injection.py` (3개)

**위치**: `tests/integration/tdd/test_dependency_injection.py`

**실패한 테스트**:
- `test_get_neo4j_storage`
- `test_get_chroma_storage`
- `test_get_composite_storage`

**원인**:
```python
# 테스트 코드 (현재)
from app.core.dependencies import get_neo4j_storage  # ❌ 잘못된 경로

# 실제 위치 (Spec 011 이후)
from app.interfaces.api.dependencies import get_neo4j_storage  # ✅ 올바른 경로
```

Spec 011에서 DI 함수들이 `app.core.dependencies` → `app.interfaces.api.dependencies`로 이동했으나, 테스트는 업데이트되지 않음.

**추가 확인 사항**:
- `app.interfaces.api.dependencies.py`에는 개별 storage getter 함수가 없고, `get_repository()`만 존재
- 테스트가 요구하는 함수들이 실제로 존재하지 않을 가능성

---

### 실패 테스트 2: `test_usecases.py` (3개)

**위치**: `tests/unit/test_usecases.py`

**실패한 테스트**:
- `test_create_job`
- `test_process_job_success`
- `test_process_job_failure`

**원인**:
```python
# 테스트 코드 (현재)
service = IngestionService(
    scraper=mock_scraper,
    repository=mock_doc_repo,
    job_repository=mock_job_repo
)  # ❌ 파라미터 부족

# 실제 생성자 (Spec 010 이후)
def __init__(
    self,
    scraper: ScraperInterface,
    repository: DocumentRepository,
    graph: GraphRepository,  # ✅ 추가됨
    job_repository: JobRepository,
    extractor: SemanticExtractor | None = None  # ✅ 추가됨
):
```

Spec 010에서 `IngestionService` 생성자에 `graph`와 `extractor` 파라미터가 추가되었으나, 테스트는 구버전 생성자를 사용 중.

## 🎯 목표

1. **DI 테스트 수정**: Import 경로 수정 및 존재하지 않는 함수 처리
2. **Use Case 테스트 수정**: Mock 설정 업데이트 (graph, extractor 추가)
3. **테스트 통과 확인**: 수정 후 전체 테스트 스위트 실행 및 검증
4. **회귀 방지**: 다른 테스트에 영향이 없는지 확인

## 📊 성공 기준

- [ ] `test_dependency_injection.py` 3개 테스트 통과
- [ ] `test_usecases.py` 3개 테스트 통과
- [ ] 전체 테스트 스위트 통과 (회귀 방지)
- [ ] CI 파이프라인 통과

## 🚫 Out of Scope

- 새로운 테스트 추가
- 프로덕션 코드 변경
- 테스트 전략 개선 (별도 Spec으로 분리)

## 📚 참고 문서

- `specs/006-clean-architecture/plan.md`
- `specs/010-knowledge-graph-construction/plan.md`
- `specs/011-infrastructure-refactoring/plan.md`
- `specs/012-integration-test-high-priority/failed_tests_analysis.md`
