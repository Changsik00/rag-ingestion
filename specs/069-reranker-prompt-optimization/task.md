# Task List: Spec-069

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

---

## Task 1: Reranker v2 Prompt 작성

### 1-1. Prompt Design
- [x] `app/domain/services/prompts/reranker_v2.py` 생성
  - Context-Aware 프롬프트 작성
  - PENALTY 규칙 제거
  - Multi-Entity Query 가이드라인 추가
  - Self-Verification 로직 추가
- [x] JSON 파싱 수동 검증
- [x] Commit: `feat(spec-069): add reranker v2 context-aware prompt` (e90b126)

### 1-2. TDD Warming up
- [x] Test Case 작성: `tests/unit/domain/prompts/test_reranker_v2.py`
  - Prompt format 검증
  - JSON 파싱 테스트
- [x] Test 실행 (Pass): `uv run pytest tests/unit/domain/prompts/test_reranker_v2.py` ✅ 6 passed
- [x] Commit: `test(spec-069): add reranker v2 prompt validation test` (f9d95c7)

---

## Task 2: Feature Flag 및 통합

### 2-1. Feature Flag 추가
- [x] `app/core/config.py`에 `RERANKER_VERSION = "v1"` 추가
- [x] Commit: `feat(spec-069): add reranker version feature flag` (47d541f)

### 2-2. Reranker Service 수정
- [x] `app/infrastructure/ai/rag_nodes.py` 수정
  - `_rerank_pointwise()` 메서드에 버전 선택 로직 추가
  - v1/v2 import 추가
- [x] Commit: `feat(spec-069): integrate reranker v2 with feature flag` (20bf4cb)

### 2-3. Integration Test
- [x] `tests/unit/infrastructure/rag/test_rag_reranker.py` 수정
  - v2 Feature Flag 테스트 추가
- [x] Test 실행 (Pass): `uv run pytest tests/unit/infrastructure/rag/test_rag_reranker.py` ✅ 2 passed
- [x] Commit: `test(spec-069): add reranker v2 integration test` (17f41d1)
- [x] `.env.example`에 RERANKER_VERSION 추가 (06fb54c)

---

## Task 3: A/B Testing 인프라

### 3-1. A/B 테스트 스크립트 작성
- [ ] `scripts/compare_reranker_versions.py` 생성
  - 10개 테스트 질문 정의
  - Recall/Precision 계산 로직
  - 결과 비교 리포트 생성
- [ ] Commit: `feat(spec-069): add reranker a/b testing script`

### 3-2. A/B 테스트 실행
- [ ] v1 Baseline 측정 및 결과 저장
- [ ] v2 실행 및 결과 저장
- [ ] 결과 비교 및 분석
- [ ] 결과를 `spec.md`에 추가
- [ ] Commit: `docs(spec-069): add a/b test results`

---

## Task 4: Verification & Decision

### 4-1. Automated Test 전체 실행
- [ ] `uv run pytest tests/unit/domain/prompts/test_reranker_v2.py`
- [ ] `uv run pytest tests/unit/infrastructure/rag/test_rag_reranker.py`
- [ ] 모든 테스트 통과 확인

### 4-2. Manual Testing
- [ ] Admin UI Playground에서 비교 질문 테스트
  - "일론 머스크의 SpaceX와 Tesla 비교"
  - "Claude와 GPT-4의 차이점"
- [ ] RAG Inspector로 Reranker 점수 확인
- [ ] v1 vs v2 체감 품질 비교

### 4-3. 의사결정
- [ ] v2 Recall +10% 이상 확인
- [ ] v2 Precision -5% 이내 확인
- [ ] v2 채택 또는 v1 유지 결정
- [ ] 결정 근거를 `spec.md`에 문서화

---

## Task 5: Deployment

### 5-1. 설정 적용
- [ ] **If v2 채택**: `config/admin_config.py`에서 `RERANKER_VERSION = "v2"` 변경
- [ ] **If v1 유지**: 원인 분석 및 개선 계획 수립
- [ ] Commit: `feat(spec-069): set reranker v2 as default` or `docs(spec-069): document v1 retention decision`

---

## Task 6: PR Creation & Archiving (Mandatory)
<!-- 이 단계는 모든 작업 완료 후 수행합니다. -->
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] **Walkthrough 작성**: `specs/069-reranker-prompt-optimization/walkthrough.md`
- [ ] **PR Description 작성**: `specs/069-reranker-prompt-optimization/pr_description.md` (템플릿 준수)
- [ ] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-069): archive walkthrough and pr description`)
- [ ] Create PR: `gh pr create --title "Spec 069: Reranker Prompt Optimization" --body-file specs/069-reranker-prompt-optimization/pr_description.md`

## Summary
**총 Task**: 6개  
**예상 커밋 수**: 9개  
**현재 진행**: Execution - Task 3 (A/B Testing 인프라)  
**완료 커밋**: 6개 (e90b126, f9d95c7, 47d541f, 20bf4cb, 06fb54c, 17f41d1, 7c03595)
