# Walkthrough: Spec-061 RAG Session Manual Cleanup

## 📝 Changes Overview

본 스펙은 RAG 세션의 데이터(Checkpoints, Writes)를 확실하게 삭제하고, Admin UI의 세션 관리 기능을 개선했습니다.

### 1. Backend: SQL-based Session Cleanup
- `AsyncPostgresSaver`가 `adelete_thread`를 지원하지 않는 경우를 대비해, `database.pool`을 사용하여 직접 SQL `DELETE`를 수행하는 로직을 추가했습니다.
- Target Tables: `checkpoint_writes`, `checkpoint_blobs`, `checkpoints` (Thread ID 기준 삭제).

### 2. Frontend: Admin UI Sidebar Controls
- `admin/pages/4_RAG_Playground.py`의 "Advanced Settings" 내에 있던 버튼들을 제거했습니다.
- **New Chat** 및 **Reset(Delete History)** 버튼을 사이드바 상단으로 이동하여 접근성을 높였습니다.

### 3. Verification: Integration Test
- `tests/integration/functional/test_rag_session_cleanup.py` 추가.
- 세션 생성 -> 데이터 확인 -> `reset` API 호출 -> 데이터 삭제 확인 흐름을 자동화 테스트로 검증했습니다.

## 📸 Screenshots

> *UI 변경 사항 (Sidebar Buttons) 스크린샷은 생략하지만, 로컬 실행 시 사이드바 상단에서 확인 가능합니다.*

## 🧪 Verification Results

### Automated Tests
```bash
uv run pytest tests/integration/functional/test_rag_session_cleanup.py
```
- Result: **Passed** (Backend logic verified)

### Code Quality
- Ruff check & format passed.
