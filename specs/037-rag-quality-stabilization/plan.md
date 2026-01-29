# Implementation Plan: Spec-037 - Document-Level Storage Integrity

## 📋 Branch Strategy
- `feature/037-document-integrity-sync`

## 🛑 User Review Required
- [x] **Document-Chunk Consistency**: `Document` 노드의 제목을 자식 `Chunk`들에게 강제로 덮어씌우는 방식(Propagate)에 대한 동의 여부.

---

## 🎯 Core Strategy

### 1. 문서 중심의 정합성 분석 (Document-Centric Analysis)
- 청크 ID만 대조하는 것이 아니라, `Document`별로 그룹화하여 **"어떤 문서가 유실되었는가"**를 파악합니다.
- `Neo4j Query`: `MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk) RETURN d.id, d.title, count(c) as total_chunks`

### 2. 메타데이터 계층적 보정 (Hierarchical Restoration)
- **Step 1**: 제목이 비어있는 `Document` 노드를 찾아 `Title Fallback` 로직 적용.
- **Step 2**: `Document`의 제목을 모든 소속 `Chunk` 노드의 `metadata.title`로 복사 (Consistency 확보).
- **Step 3**: 보정된 `Chunk`를 ChromaDB로 Push.

---

## 📂 Proposed Changes

### [Domain Layer]
#### [MODIFY] `app/domain/services/storage_integrity_service.py`
- `get_document_drift_report()`: 문서별 인덱싱 상태(전체/부분/누락) 리포트 생성 로직 추가.

### [Infrastructure Layer]
#### [MODIFY] `app/infrastructure/rag/nodes.py`
- `generate_answer` 노드에서 사용되는 컨텍스트 정제 로직 유지.

### [Admin Dashboard]
#### [NEW] `app/admin/pages/5_Storage_Management.py`
```python
# UI Mockup Logic
st.title("📂 Document Integrity Manager")

# 1. 문서 단위 리포트
drift_df = service.get_document_drift_report()
st.table(drift_df) # Columns: Title, Chroma/Neo4j Ratio, Action

# 2. 문서 선택 시 청크 상세 조회
if selected_doc:
    chunks_df = service.get_chunks_for_document(selected_doc)
    st.dataframe(chunks_df)
    if st.button("Fix This Document"):
        service.sync_document(selected_doc)
```

---

## 🧪 Verification Plan

### Automated Tests
- `test_document_title_propagation`: 문서 제목이 자식 청크들에게 올바르게 전파되는지 검증.
- `test_drift_report_calculation`: 문서별 인덱싱 비율 계산 정확성 검증.

### Manual Verification
1. Admin 대시보드에서 "인덱싱 0%"인 문서를 식별.
2. 해당 문서의 "Fix" 버튼 클릭 후 ChromaDB에 해당 문서의 청크들이 정상적으로 올라가는지 확인.
3. RAG Playground에서 해당 문서 제목으로 필터링하여 검색이 잘 되는지 확인.
