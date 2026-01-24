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

## Task 1: Document Integrity & Stats (Core)

### 1-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/domain/services/test_storage_integrity.py`
  - 문서별 청크 개수(Total vs Indexed) 비교 로직 검증
  - 제목 전파(Title Propagation: Document -> Chunk) 로직 검증
- [x] Test 실행 (Pass): `uv run pytest tests/unit/domain/services/test_storage_integrity.py`
- [x] Commit: `test(spec-037): add tests for document-level drift analysis and title propagation`

### 1-2. Implementation
- [x] 코드 구현: `app/domain/services/storage_integrity_service.py`
  - [x] `get_drift_report()`: 전체 ID 대조 및 통계
  - [x] `get_document_drift_report()`: 문서별 인덱싱 통계 산출
  - [x] `propagate_document_metadata()`: 상위 문서 정보를 하위 청크로 동기화
- [x] Test 실행 (Pass): `uv run pytest tests/unit/domain/services/test_storage_integrity.py`
- [x] Commit: `feat(spec-037): implement document-centric integrity analysis and metadata sync`

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

## Summary
**총 Task**: 모든 구현 단계 완료
**최종 상태**: 단위 테스트 통과 및 Admin UI 신설 완료.
