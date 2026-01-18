# Failed Tests Analysis (2026-01-18)

## 🚨 현재 실패 테스트: 6개

### 1. test_dependency_injection.py (3개 실패)

**위치:** `tests/integration/tdd/test_dependency_injection.py`

**실패한 테스트:**
- `test_get_neo4j_storage`
- `test_get_chroma_storage`
- `test_get_composite_storage`

**가능한 원인:**
- DI 설정이 변경되었으나 테스트가 업데이트되지 않음
- Protocol 기반으로 변경 후 테스트 수정 누락 (Spec 006)
- Import 경로 변경 후 테스트 미업데이트 (Spec 011)

**우선순위:** High (DI는 핵심 기능)

---

### 2. test_usecases.py (3개 실패)

**위치:** `tests/unit/test_usecases.py`

**실패한 테스트:**
- `test_create_job`
- `test_process_job_success`
- `test_process_job_failure`

**가능한 원인:**
- `IngestionService` 생성자가 변경됨 (GraphRepository 추가, Spec 010)
- Mock 설정이 구버전 signature 사용
- TypeError: IngestionService 파라미터 불일치

**우선순위:** High (Core Use Case 테스트)

---

## 📋 해결 방안

### Option A: 즉시 수정 (다음 Spec으로)
- **Spec 013: Fix Failed Tests**
- 6개 테스트 수정
- DI 및 Use Case 테스트 복구

### Option B: Icebox에 등록
- 우선순위: High
- 향후 리팩토링과 함께 수정

---

## 🔗 관련 Spec

**원인이 된 Spec:**
- Spec 006: Clean Architecture Refactoring (Protocol 도입)
- Spec 010: Knowledge Graph Construction (GraphRepository 추가)
- Spec 011: Infrastructure Refactoring (Import 경로 변경)

---

**작성일:** 2026-01-18  
**발견 시점:** Spec 012 테스트 실행 중
