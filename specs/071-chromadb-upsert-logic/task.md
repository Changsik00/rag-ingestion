# Task List: Spec-071

## Progress
- [ ] Spec 번호 확정 및 브랜치 생성
- [ ] spec.md 작성
- [ ] plan.md 작성
- [ ] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

---

## Task 1: 브랜치 생성 및 환경 확인

### 1-1. Feature 브랜치 생성
- [ ] 브랜치 생성: `git checkout -b feature/071-chromadb-upsert-logic`
- [ ] 브랜치 확인: `git branch --show-current`
- [ ] Commit: `chore(spec-071): create feature branch for chromadb upsert logic`

### 1-2. ChromaDB API 확인
- [ ] ChromaDB 버전 확인: `uv pip list | grep chromadb`
- [ ] `upsert` 메서드 지원 여부 확인 (Python Shell 또는 문서 참조)
- [ ] 기존 테스트 실행: `uv run pytest tests/unit/infrastructure/repositories/test_chroma.py -v`

---

## Task 2: Integration Test 작성 (TDD)

### 2-1. Test Case 작성
- [ ] 파일 생성: `tests/integration/test_duplicate_ingestion.py`
- [ ] Test 케이스 구현:
  - `test_duplicate_document_upsert()`: 동일 문서 2번 수집 시 중복 저장 없음
  - `test_neo4j_chroma_consistency()`: Neo4j ↔ ChromaDB 데이터 일관성
  - `test_metadata_update()`: 메타데이터 업데이트 정상 반영
- [ ] Test 실행 (Fail 예상): `uv run pytest tests/integration/test_duplicate_ingestion.py -v`
- [ ] Commit: `test(spec-071): add integration test for duplicate ingestion`

---

## Task 3: ChromaDB Repository Upsert 로직 구현

### 3-1. `save()` 메서드 수정
- [ ] `app/infrastructure/repositories/chroma.py:102` 수정
- [ ] `collection.add` → `collection.upsert` 변경
- [ ] 로컬 테스트: `uv run pytest tests/unit/infrastructure/repositories/test_chroma.py::test_save -v`

### 3-2. `save_chunks()` 메서드 수정
- [ ] `app/infrastructure/repositories/chroma.py:152` 수정
- [ ] `collection.add` → `collection.upsert` 변경
- [ ] 로컬 테스트: `uv run pytest tests/unit/infrastructure/repositories/test_chroma.py::test_save_chunks -v`

### 3-3. 전체 테스트 실행
- [ ] Integration Test 통과 확인: `uv run pytest tests/integration/test_duplicate_ingestion.py -v`
- [ ] 전체 테스트 통과: `uv run pytest`
- [ ] Commit: `feat(spec-071): replace chromadb add with upsert for duplicate prevention`

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

---

## Task 5: Code Quality 및 Cleanup

### 5-1. Code Quality Check
- [ ] Ruff 검사: `uv run ruff check . --fix`
- [ ] Ruff 포맷: `uv run ruff format .`
- [ ] 전체 테스트 재실행: `uv run pytest`

### 5-2. Commit Cleanup
- [ ] 필요 시 커밋 정리: `git rebase -i HEAD~N`
- [ ] 최종 커밋 메시지 확인

---

## Task 6: PR Creation & Archiving (Mandatory)

### 6-1. Walkthrough 작성
- [ ] `specs/071-chromadb-upsert-logic/walkthrough.md` 작성
  - 구현 내용 요약
  - Integration Test 결과
  - Manual Verification 증거 (스크린샷)

### 6-2. PR Description 작성
- [ ] 템플릿 읽기: `docs/templates/pr_description.md`
- [ ] `specs/071-chromadb-upsert-logic/pr_description.md` 작성 (Template 준수, 한국어)
- [ ] PR Title 확인: `feat(spec-071): chromadb upsert logic for duplicate prevention`

### 6-3. Archive Commit
- [ ] Archive Commit: `git add specs/071-chromadb-upsert-logic/walkthrough.md specs/071-chromadb-upsert-logic/pr_description.md`
- [ ] Commit: `docs(spec-071): archive walkthrough and pr description`
- [ ] Push: `git push -u origin feature/071-chromadb-upsert-logic`

### 6-4. Create PR
- [ ] PR 생성: `gh pr create --title "feat(spec-071): chromadb upsert logic for duplicate prevention" --body-file specs/071-chromadb-upsert-logic/pr_description.md`
- [ ] PR 링크 확인 및 리뷰 요청

---

## Summary

**총 Task**: 6개  
**예상 커밋 수**: 5개  
- `chore(spec-071): create feature branch`
- `test(spec-071): add integration test for duplicate ingestion`
- `feat(spec-071): replace chromadb add with upsert`
- `docs(spec-071): archive walkthrough and pr description`
- (Optional) Cleanup commits

**현재 진행**: Planning  
**다음 단계**: User Plan Accept 대기 → Execution 시작
