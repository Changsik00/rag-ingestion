# Task List: Spec-074

## Progress
- [x] Spec 번호 확정 및 브랜치 생성 (명칭 확정)
- [x] spec.md 작성 (Template 준수)
- [x] plan.md 작성 (Template 준수)
- [/] task.md 작성 (Template 준수)
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

---

## Task 1: 인프라 준비 및 도메인 인터페이스 정의
### 1-1. Branch Setup
- [x] 브랜치 생성: `git checkout -b feature/074-llm-interface-compliance`

### 1-2. Domain Interface Implementation
- [x] 파일 생성: `app/domain/interfaces/llm_interface.py`
- [x] `LLMInterface` 및 관련 클래스 코드 이동
- [x] Commit: `feat(spec-074): move LLMInterface to domain layer`

---

## Task 2: 참조 수정 및 의존성 위반 해결
### 2-1. Domain Services Update
- [x] `app/domain/services/intent_classifier.py` 임포트 수정
- [x] `app/domain/services/query_rewriter.py` 임포트 수정
- [x] 검증: `uv run ruff check app/domain`
- [x] 단위 테스트 통과: `pytest tests/unit/domain/services/`
- [x] Commit: `refactor(spec-074): fix domain layer dependency violations`

### 2-2. Cross-Layer References Update
- [x] `app/application/services/semantic_extractor.py` 등 애플리케이션 레이어 수정
- [x] `app/infrastructure/ai/` 등 인프라 레이어 수정
- [x] Commit: `refactor(spec-074): update all LLMInterface import paths`

---

### 2-3. Test References Update (Troubleshooting)
- [x] 테스트 코드 내의 임포트 참조 수정 (`sed` 이용 전수 수정)
- [x] 전체 테스트 재실행 및 확인
### 3-1. Cleanup
- [x] `app/application/interfaces/llm.py` 삭제
- [x] Commit: `cleanup(spec-074): remove legacy LLM interface file`

---

## Task 4: PR Creation & Archiving (Mandatory)
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] **Walkthrough 작성**: `specs/074-llm-interface-clean-architecture/walkthrough.md`
- [ ] **PR Description 작성**: `specs/074-llm-interface-clean-architecture/pr_description.md`
- [ ] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-074): archive walkthrough and pr description`)
- [ ] Create PR: `gh pr create --title "feat(spec-074): llm interface clean architecture compliance" --body-file specs/074-llm-interface-clean-architecture/pr_description.md`

## Summary
**총 Task**: 4개  
**예상 커밋 수**: 5~6개  
**현재 진행**: Planning
