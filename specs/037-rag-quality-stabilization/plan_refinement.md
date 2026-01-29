# Implementation Plan: Spec-037 - Admin UI & Performance Refinement

## 📋 Summary
기존 Admin UI의 레이아웃을 개선하여 진단(분석)이 먼저 나오고 조치(복구)가 나중에 나오도록 변경합니다. 또한, N+1 쿼리 문제를 해결하여 성능을 최적화하고, 데이터 불일치의 세부 내용(스니펫)을 확인할 수 있는 기능을 추가합니다.

## 🛑 User Review Required
- [x] **Button Semantics**: "Fix All Chunks" 버튼의 색상이 'Primary'(테마에 따라 빨간색/오렌지색)로 표시되는 것이 의도된 것인지 재확인 (중요 액션이므로 눈에 띄게 설정함).
- [x] **Data Preview**: 청크 미리보기를 테이블 내 Expander로 넣을지, 별도 팝업으로 처리할지를 결정 (현재는 Expander 제안).

---

## 🎯 Core Strategy

### 1. Performance Optimization (N+1 해결)
- `StorageIntegrityService.get_document_drift_report()`가 1000번의 쿼리를 날리는 대신, Neo4j에서 한 번의 집계 쿼리로 문서별 청크 개수를 가져오도록 수정합니다.

### 2. UI Layout & UX (분석 후 조치)
- **레이아웃 순서**: Metrics -> **Drift Report (상세 분석)** -> **Recovery Actions (하단 배치)**.
- **다이나믹 버튼 스타일링**: 
  - **Mismatches 존재 시**: "Run Global Sync" 버튼을 **빨간색 (`type="primary"`)**으로 설정하여 강력하게 조치를 상기시킵니다.
  - **Mismatches 부재 시**: 버튼을 **중립색 (`type="secondary"`)**으로 설정합니다.
- **임시 버튼 제거**: 사용자 혼란을 주는 "test only" 관련 잔재가 있다면 완전히 제거.
분석 결과를 토대로 실행.

### 3. Visibility of Mismatches
- 테이블 각 행에 'View Missing Snippets' 섹션을 추가하여 실제로 어떤 텍스트가 누락되었는지 확인 가능하게 함.

---

## 📂 Proposed Changes

### [Domain Layer]
#### [MODIFY] `app/domain/services/storage_integrity_service.py`
- `get_document_drift_report()`: Neo4j 집계 쿼리를 사용하여 최적화.
- `get_missing_snippets(doc_id)`: 특정 문서의 누락된 청크 본문을 가져오는 메서드 추가.

### [Infrastructure Layer]
#### [MODIFY] `app/infrastructure/storage/neo4j_document_repository.py`
- `get_document_counts()`: 문서 ID별 청크 개수를 반환하는 효율적인 쿼리 추가.

### [Admin Dashboard]
#### [MODIFY] `app/admin/pages/5_Storage_Management.py`
- 레이아웃 재배치 (Report -> Actions).
- 혼란스러운 버튼명 및 색상 정리 (`type="primary"` 선택적 사용).
- 상세 보기(Expander) 기능 강화.

---

## 🧪 Verification Plan

### Automated Tests
- `test_get_document_counts`: Neo4j에서 문서별 청크 개수 집계가 정확한지 확인.
- `pytest tests/unit/domain/services/test_storage_integrity.py`

### Manual Verification
1. **성능 확인**: 페이지 로딩이 N+1 쿼리 때보다 확연히 빨라졌는지 확인.
2. **레이아웃 확인**: 요약 -> 상세 리포트 -> 하단 복구 버튼 순으로 배치가 바뀌었는지 확인.
3. **미리보기 확인**: 표에서 특정 문서를 펼쳤을 때 어떤 부분이 누락되었는지 텍스트 스니펫이 보이는지 확인.
