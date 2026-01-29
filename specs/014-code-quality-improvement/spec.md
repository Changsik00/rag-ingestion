# Spec 014: Code Quality Improvement

## 📋 요약

코드 품질 개선을 위한 두 가지 작업을 수행합니다:
1. **Bug Fix**: `semantic_data` undefined 버그 수정
2. **Test Standardization**: TDD 테스트 GWT (Given-When-Then) 형식 통일

## 🎯 Background

###  1. semantic_data 버그 (Spec 013에서 발견)

**위치:** `app/use_cases/ingestion.py` Line 74

**문제:**
```python
# Line 52-61: semantic_data는 if self.extractor 안에서만 정의됨
if self.extractor:
    try:
        semantic_data = self.extractor.extract(result.markdown)
        # ...
    except Exception as e:
        print(f"Semantic extraction failed for job {job_id}: {e}")

# Line 74: extractor=None이면 semantic_data가 정의되지 않아 NameError 발생
if semantic_data and semantic_data.entities:  # ❌ NameError 가능
    self._build_knowledge_graph(doc.id, semantic_data.entities)
```

**영향:**
- `extractor=None`으로 `IngestionService` 생성 시 `NameError` 발생
- Spec 013에서 테스트만 우회했지만 프로덕션 버그는 여전히 존재

---

### 2. TDD 테스트 GWT 형식 불일치

**현재 상태:**
- ✅ **BDD 테스트**: 모두 GWT 형식 적용
- ✅ **일부 TDD 테스트**: GWT 형식 적용 (`test_dependency_injection.py`)
- ❌ **Unit 테스트**: GWT 형식 미적용 (6개 파일)

**적용 필요 파일:**
1. `tests/unit/test_job_entity.py`
2. `tests/unit/test_neo4j_graph_repository.py`
3. `tests/unit/test_neo4j_job_repo.py`
4. `tests/unit/test_scraper.py`
5. `tests/unit/test_storage.py`
6. `tests/unit/test_usecases.py`
7. `tests/integration/tdd/test_api_ingest.py`
8. `tests/integration/tdd/test_async_ingest.py`
9. `tests/integration/tdd/test_jobs.py`

---

## 🔍 분석

### Bug Fix 전략

**Option A: Initialize semantic_data = None**
```python
semantic_data = None  # 초기화
if self.extractor:
    try:
        semantic_data = self.extractor.extract(result.markdown)
        # ...
```

**Option B: Nested if check**
```python
if self.extractor:
    try:
        semantic_data = self.extractor.extract(result.markdown)
        # ...
        
        # 여기서 바로 graph 구축
        if semantic_data and semantic_data.entities:
            self._build_knowledge_graph(doc.id, semantic_data.entities)
```

**선택: Option A** (더 명확하고 읽기 쉬움)

---

### GWT 표준화 전략

**표준 형식:**
```python
def test_example():
    # Given: 테스트 조건 설명
    mock_obj = Mock()
    
    # When: 테스트할 동작
    result = function(mock_obj)
    
    # Then: 기대 결과
    assert result == expected
```

---

## 🎯 목표

1. **Bug Fix**: `semantic_data` 버그 수정 및 테스트 추가
2. **Test Standardization**: 9개 TDD 테스트 파일 GWT 형식 통일
3. **전체 테스트 통과**: 회귀 방지 확인

---

## 📊 성공 기준

- [x] `semantic_data` 버그 수정 완료
- [x] 9개 TDD 테스트 파일 GWT 형식 적용
- [x] 전체 테스트 스위트 통과 (회귀 없음)
- [x] CI 통과 (if exists)

---

## 🚫 Out of Scope

- BDD 테스트는 이미 GWT 적용되어 있으므로 제외
- 새로운 테스트 추가는 하지 않음
- 프로덕션 로직 변경 (버그 수정 외)

---

## 📚 참고 문서

- `app/use_cases/ingestion.py` (Line 74 버그)
- `specs/013-fix-failed-tests/` (버그 발견 경위)
- BDD 테스트 파일들 (GWT 형식 참고 예시)
