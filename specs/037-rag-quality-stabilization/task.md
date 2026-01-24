# Task List: Spec-037 - RAG Quality & Storage Integrity

## Progress
- [x] Spec 번호 확정 (037)
- [x] spec.md 상세화 (Document-level 요구사항 추가)
- [x] plan.md 상세화 (문서 중심 동기화 및 전파 설계)
- [x] task.md 리팩토링 (Document 단위 태스크 분할)
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept
- [x] Feature 브랜치 생성: `feature/037-rag-storage-integrity`

---

## 🎯 Core Strategy

### 1. Performance Optimization (N+1 해결)
- **Cypher 최적화**: `MATCH (d:Document) OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk) RETURN d.id, d.metadata.title, count(c)` 쿼리를 사용하여 문서별 청크 개수를 한 번에 산출.
- **Batch Metadata Check**: ChromaDB에서 모든 ID를 한 번만 가져와서 메모리에서 대조 (기존 방식 유지하되 데이터 구조 효율화).

### 2. UI Layout & UX (분석 후 조치)
- **레이아웃 순서**: Metrics -> **Drift Report (상세 분석)** -> **Recovery Actions (하단 배치)**.
- **버튼 스타일링**: 
  - "Run Global Sync": `type="secondary"` (기본색)로 변경하여 공포감(?) 해소.
  - "Fix Document": 테이블 내 Action 버튼으로 배치 고려.
- **임시 버튼 제거**: 사용자 혼란을 주는 "test only" 관련 잔재가 있다면 완전히 제거.

### 3. Visibility of Mismatches (세부 내용 확인)
- 특정 문서 행 클릭 시 **"누락된 문장(Chunk Snippet)"**을 바로 확인할 수 있는 Expander 기능 추가.

---

## 📂 Proposed Changes

### [Infrastructure Layer]
#### [MODIFY] `app/infrastructure/storage/neo4j_document_repository.py`
- `get_document_stats()` 메서드 추가: Cypher 집계 쿼리 구현.

### [Domain Layer]
#### [MODIFY] `app/domain/services/storage_integrity_service.py`
- `get_document_drift_report()`: 新 집계 메서드 사용하여 리팩토링.
- `get_missing_chunk_previews(doc_id)`: 누락된 청크 본문 상위 300자 반환 로직 추가.

### [Admin Dashboard]
#### [MODIFY] `app/admin/pages/5_Storage_Management.py`
- 최하단으로 'Recovery Actions' 이동.
- 데이터프레임 하단에 '선택 문서 상세 보기' 배치.

---

## Task 2: Advanced Sync Engine (Selective Sync)

### 2-1. Implementation
- [x] 코드 구현: `scripts/sync_indices.py` 전면 고도화
  - [x] 문서 단위 동기화 및 일괄 보정 기능 통합
- [x] Commit: `feat(spec-037): upgrade sync engine to support selective and hierarchical recovery`

---

## Task 3: Document-Centric Admin UI

### 3-1. Management Interface
- [x] 코드 구현: `app/admin/pages/5_Storage_Management.py`
  - **Document Indexing Report**: 문서별 인덱싱 비율(%) 및 상태 시각화
  - **Action Menu**: 문서별 "Fix Metadata", "Sync to Chroma" 버튼 배치
  - **Chunk Preview**: 특정 문서 선택 시 소속 청크 내용 미리보기
- [x] Commit: `feat(spec-037): add document-centric management UI to admin dashboard`

---

## Task 4: Brain Quality Gate (Context Cleaning)

### 4-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/infrastructure/rag/test_context_cleaning.py`
- [x] Test 실행 (Pass): `uv run pytest tests/unit/infrastructure/rag/test_context_cleaning.py`
- [x] Commit: `test(spec-037): add tests for RAG context noise cleaning`

### 4-2. Implementation
- [x] 코드 구현: `app/infrastructure/rag/nodes.py` 내 `generate_answer` 노드 수정
- [x] Commit: `feat(spec-037): integrate regex-based cleaning gate into RAG nodes`

---

## Task 5: Admin UI Refinement & Optimization
### 5-1. Performance (N+1 Fix)
- [x] `Neo4jStorage.get_document_stats()` 및 `get_all_chunk_metadata()` 벌크 조회 구현
- [x] `StorageIntegrityService` N+1 쿼리 제거 (Bulk Load 방식으로 전환)
- [x] Commit: `perf(spec-037): ultra-optimize drift report with bulk metadata retrieval`

### 5-2. UX & Layout Improvement
- [x] 'Missing Title' 상태 정의 및 리포트 가시화 (정지되었던 리포트 문제 해결)
- [x] 버튼 활성화 로직 수정 (제목 누락 시에도 복구 버튼 활성화)
- [x] Missing Chunk Snippet 시각화 (상세 진단 기능 추가)
- [x] Commit: `fix(spec-037): resolve UI rendering issues and enhance document drift status`

---

## Summary
**총 Task**: 9개 주요 항목 (Refinement 추가됨)
**최종 상태**: 초기 구현 완료, 사용자 피드백 기반 리팩토링 진행 중.
