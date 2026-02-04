# Task List: Spec-063

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] tasks.md 작성
- [x] User Plan Accept

---

## Task 1: Verification Lab Implementation
### 1-1. Create Verification Lab Page
- [x] 코드 구현: `admin/pages/5_Verification_Lab.py` 생성.
  - `manual_rag_verification.py` 로직 이식.
  - Question Input Form, Run Button, Result Display (Answer, Sources).
- [x] Manual Verification: Admin 실행 후 페이지 동작 확인.
- [x] Commit: `feat(spec-063): add verification lab page`

---

## Task 2: Graph Explorer Improvements
### 2-1. Fix Preset Loading
- [x] 코드 수정: `admin/pages/1_Graph_Explorer.py`
  - `st.text_area`에 `key` 추가.
  - Preset Load Button 콜백에서 Session State 업데이트 로직 수정.
- [x] Manual Verification: Preset 로드 시 쿼리 텍스트 즉시 변경 확인.

### 2-2. Dark Mode Support & Style Update
- [x] 코드 수정: `admin/pages/1_Graph_Explorer.py`
  - Node Color/Font Config 수정 (Dark Mode 대응).
  - Edge Color 수정 (가시성 확보).
- [x] Manual Verification: Dark Mode에서 가독성 확인.
- [x] Commit: `feat(spec-063): improve graph explorer ux`

---

## Task 3: Feedback Integration & Wrap-up
### 3-1. Verify Feedback Feature
- [x] 코드 검토/수정: `admin/pages/4_RAG_Playground.py`
  - Feedback API 호출 성공/실패 처리 로직 보강.
- [x] Manual Verification: Feedback 버튼 클릭 시 동작 확인.
- [x] Commit: `fix(spec-063): enhance feedback ui robustness`

### 3-2. Documentation & PR
- [x] Walkthrough 작성: `specs/spec-063-frontend-ux-improvements/walkthrough.md`
- [x] Version Bump & Archive: PR Description 작성.
- [x] Bug Fixes (Post-PR):
  - [x] `st.text_area` value warning fix.
  - [x] Graph Preset unwrapping fix.
  - [x] Graph Edge visibility fix (Dark Mode toggle).
- [ ] PR URL: [feat(spec-063): admin ui/ux improvements #70](https://github.com/Changsik00/rag-ingestion/pull/70) `specs/spec-063-frontend-ux-improvements/pr_description.md`
- [ ] Archive Commit: `docs(spec-063): archive walkthrough`
- [ ] PR Creation: `gh pr create`

## Summary
**총 Task**: 3개 Phase
**예상 커밋 수**: 4~5개
**현재 진행**: Planning
