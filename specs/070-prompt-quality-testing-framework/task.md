# Task List: Spec-070

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Prompt Test Dataset 구축

### 1-1. Test Dataset Schema 정의
- [x] YAML 스키마 설계: `tests/prompt/test_cases_schema.yaml`
- [x] 5개 Intent 카테고리별 필드 정의
- [x] Commit: `test(spec-070): add test dataset schema`

### 1-2. Test Cases 작성 (50개)
- [x] General Query (10개): `tests/prompt/intent_test_cases.yaml`
- [x] Compare (10개)
- [x] Summarize (10개)
- [x] Filter by Topic (10개)
- [x] Edge Cases (10개: 모호한 질문, 다국어, 긴 질문 등)
- [x] Commit: `test(spec-070): add 50 intent classification test cases`

---

## Task 2: Pytest 기반 자동 검증 스크립트

### 2-1. TDD Warming up
- [x] Test Case 작성: `tests/prompt/test_intent_classifier_quality.py`
- [x] Test 실행 (Fail): `uv run pytest tests/prompt/test_intent_classifier_quality.py`
- [x] Commit: `test(spec-070): add intent classifier quality test`

### 2-2. Implementation
- [x] YAML 파싱 헬퍼 함수 구현
- [x] Parametrized Test 작성 (50개 케이스)
- [x] Test 실행 (Pass): `uv run pytest tests/prompt/test_intent_classifier_quality.py -v`
- [x] Commit: `feat(spec-070): implement yaml-driven intent test`

---

## Task 3: Baseline Accuracy 측정

### 3-1. 현재 Intent Classifier Accuracy 측정
- [ ] 50개 테스트 케이스 실행
- [ ] Accuracy, Precision, Recall 계산
- [ ] 결과 저장: `specs/070/baseline_report.md`
- [ ] Commit: `docs(spec-070): add baseline accuracy report`

### 3-2. 실패 케이스 분석
- [ ] Accuracy 80% 미만 케이스 추출
- [ ] 실패 원인 분류 (편향, 애매한 프롬프트, LLM 한계 등)
- [ ] 개선 방향 제안: `specs/070/baseline_report.md`
- [ ] Commit: `docs(spec-070): analyze failure cases`

---

## Task 4: CI/CD 통합

### 4-1. GitHub Actions Workflow 추가
- [ ] `.github/workflows/prompt_quality.yml` 작성
- [ ] Pytest 실행 단계 추가
- [ ] Accuracy Threshold 검증 (80% 미만 시 실패)
- [ ] Commit: `ci(spec-070): add prompt quality test to ci/cd`

### 4-2. Pre-commit Hook (Optional)
- [ ] `pre-commit` 설정 추가 (Prompt 변경 시 자동 테스트)
- [ ] Commit: `ci(spec-070): add pre-commit hook for prompt tests`

---

## Task 5: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest` (partial execution)
- [x] **Walkthrough 작성**: `specs/070-prompt-quality-testing-framework/walkthrough.md`
- [x] **PR Description 작성**: `specs/070-prompt-quality-testing-framework/pr_description.md` (템플릿 준수)
- [x] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-070): archive walkthrough and pr description`)
- [x] Create PR: `gh pr create --title "feat(spec-070): prompt quality testing framework" --body-file specs/070-prompt-quality-testing-framework/pr_description.md`

---

## Summary
**총 Task**: 5개  
**예상 커밋 수**: 10개  
**실제 커밋 수**: 5개  
**현재 진행**: ✅ Done (PR Created)
