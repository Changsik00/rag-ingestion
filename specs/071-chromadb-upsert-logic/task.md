# Task List: Spec-071

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: 브랜치 생성 및 환경 확인

### 1-1. Feature 브랜치 생성
- [x] 브랜치 생성: `git checkout -b feature/071-chromadb-upsert-logic`
- [x] 브랜치 확인: `git branch --show-current`
- [x] Commit: `chore(spec-071): create feature branch for chromadb upsert logic`

### 1-2. ChromaDB API 확인
- [x] ChromaDB 버전 확인: `uv pip list | grep chromadb`
- [x] `upsert` 메서드 지원 여부 확인 (Python Shell 또는 문서 참조)
- [x] 기존 테스트 실행: `uv run pytest tests/unit/infrastructure/repositories/test_chroma.py -v`

---

## Task 2: Integration Test 작성 (TDD)

### 2-1. Test Case 작성
- [x] 파일 생성: `tests/integration/test_duplicate_ingestion.py`
- [x] Test 케이스 구현:
  - `test_duplicate_document_upsert()`: 동일 문서 2번 수집 시 중복 저장 없음
  - `test_duplicate_chunks_upsert()`: Chunk 중복 수집 검증
  - `test_batch_chunks_upsert()`: 배치 청크 중복 방지
- [x] Test 실행 (Fail 예상): `uv run pytest tests/integration/test_duplicate_ingestion.py -v`
- [x] Commit: `test(spec-071): add integration test for duplicate ingestion`

---

## Task 3: ChromaDB Repository Upsert 로직 구현

### 3-1. `save()` 메서드 수정
- [x] `app/infrastructure/repositories/chroma.py:102` 수정
- [x] `collection.add` → `collection.upsert` 변경
- [x] Unit Test Mock 검증 수정

### 3-2. `save_chunks()` 메서드 수정
- [x] `app/infrastructure/repositories/chroma.py:152` 수정
- [x] `collection.add` → `collection.upsert` 변경
- [x] Unit Test 통과 확인

### 3-3. 전체 테스트 실행
- [x] Integration Test 통과 확인: `uv run pytest tests/integration/test_duplicate_ingestion.py -v`
- [x] Unit Test 통과 확인 (4 passed)
- [x] Commit: `feat(spec-071): replace chromadb add with upsert for duplicate prevention`

---

## Task 4: Manual Verification

### 4-1. Docker 환경 테스트
- [ ] Docker Compose 시작: `docker compose up -d`
- [ ] Admin UI 접속: `http://localhost:8501`
- [ ] 동일 URL 2번 수집 테스트 (예: Wikipedia 일론 머스크 페이지)
- [ ] ChromaDB 데이터 중복 없음 확인

### 4-2. 검증 결과 문서화
- [ ] 스크린샷 캡처: Admin UI 수집 결과
- [ ] ChromaDB 데이터 조회 결과 저장
- [ ] `specs/071-chromadb-upsert-logic/verification_result.md` 작성

> **Note**: Manual Verification은 PR 머지 전 선택적으로 수행 가능 (Automated Test로 커버됨)

---

## Task 5: Code Quality 및 Cleanup

### 5-1. Code Quality Check
- [x] Ruff 검사: `uv run ruff check . --fix`
- [x] Ruff 포맷: `uv run ruff format .`
- [x] Test Fixture 개선 (테스트 전 컬렉션 리셋)
- [x] Commit: `test(spec-071): fix test fixture to reset collection before each test`

### 5-2. Commit Cleanup
- [x] 최종 커밋 메시지 확인 (5개 커밋)

---

## Task 6: PR Creation & Archiving (Mandatory)

### 6-1. Walkthrough 작성
- [x] `specs/071-chromadb-upsert-logic/walkthrough.md` 작성
  - 구현 내용 요약
  - Integration Test 결과
  - Before/After 비교

### 6-2. PR Description 작성
- [x] 템플릿 읽기: `docs/templates/pr_description.md`
- [x] `specs/071-chromadb-upsert-logic/pr_description.md` 작성 (Template 준수, 한국어)
- [x] PR Title 확인: `feat(spec-071): chromadb upsert logic for duplicate prevention`

### 6-3. Archive Commit
- [x] Archive Commit: `git add specs/071-chromadb-upsert-logic/walkthrough.md specs/071-chromadb-upsert-logic/pr_description.md`
- [x] Commit: `docs(spec-071): archive walkthrough and pr description`
- [x] Push: `git push -u origin feature/071-chromadb-upsert-logic`

### 6-4. Create PR
- [x] PR 생성: `gh pr create --title "feat(spec-071): chromadb upsert logic for duplicate prevention" --body-file specs/071-chromadb-upsert-logic/pr_description.md`
- [x] PR #77 생성 완료: https://github.com/Changsik00/rag-ingestion/pull/77

---

## Summary

**총 Task**: 6개 (✅ 완료)  
**커밋 수**: 5개  
1. `chore(spec-071): create feature branch for chromadb upsert logic`
2. `test(spec-071): add integration test for duplicate ingestion`
3. `feat(spec-071): replace chromadb add with upsert for duplicate prevention`
4. `test(spec-071): fix test fixture to reset collection before each test`
5. `docs(spec-071): archive walkthrough and pr description`

**현재 진행**: ✅ 완료  
**PR**: #77 생성 완료 - https://github.com/Changsik00/rag-ingestion/pull/77
