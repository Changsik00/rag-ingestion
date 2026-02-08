# feat(spec-069): Reranker Prompt Optimization

## 📋 Summary

### 배경 및 목적
Spec 068에서 식별된 Reranker PENALTY 규칙의 Over-filtering 문제를 해결하여 Recall을 개선하고, Multi-Entity Query(비교 질문) 성능을 향상시킵니다.

**문제점**:
- 기존 v1 프롬프트의 PENALTY 규칙이 관련 있는 정보를 잘못 걸러냄
- "일론 머스크의 SpaceX와 Tesla 비교" 질문에서 두 엔티티 모두 낮은 점수 받음
- Context가 다르다는 이유로 관련 정보를 제외시킴

**해결 방안**:
- Context-Aware 평가 기준을 가진 v2 프롬프트 도입
- Feature Flag 시스템으로 안전한 A/B 테스트 지원
- 코드 변경 없이 .env 파일로 버전 전환 가능

### 주요 변경 사항
- [x] Reranker v2 프롬프트 작성 (PENALTY 규칙 제거, Context-Aware 평가)
- [x] Feature Flag 시스템 구축 (RERANKER_VERSION)
- [x] RAG Nodes 통합 (버전 선택 로직)
- [x] Prompt Validation 테스트 6개 작성
- [x] Integration Test 2개 작성
- [x] A/B Testing 인프라 구축 (스크립트 2개)

## 🎯 Key Review Points

1. **Reranker v2 Prompt** ([`reranker_v2.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/services/prompts/reranker_v2.py))
   - PENALTY 규칙 제거가 적절한지 검토
   - Context-Aware 평가 기준 (Multi-Entity, Name Mentions, Self-Verification)의 타당성 검증

2. **Feature Flag 구현** ([`config.py`](file:///Users/ck/Project/doit/rag-ingestion/app/core/config.py#L41-L42), [`rag_nodes.py`](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/ai/rag_nodes.py#L343-L345))
   - 버전 선택 로직의 안전성 확인
   - 롤백 가능성 검토

3. **A/B Testing Scripts** ([`compare_reranker_versions.py`](file:///Users/ck/Project/doit/rag-ingestion/scripts/compare_reranker_versions.py))
   - 10개 테스트 질문의 충분성 및 다양성 검토
   - Recall/Precision 계산 로직 검증

## 🧪 Verification

### Automated Tests
```bash
# Prompt Validation Tests
uv run pytest tests/unit/domain/prompts/test_reranker_v2.py -v
# Result: 6/6 passed ✅

# Integration Tests
uv run pytest tests/unit/infrastructure/rag/test_rag_reranker.py -v
# Result: 2/2 passed ✅

# Total: 8/8 passed ✅
```

**테스트 결과 요약:**
- ✅ `test_reranker_v2_prompt_exists`: v2 프롬프트 존재 확인
- ✅ `test_reranker_v2_prompt_format`: 프롬프트 형식 및 파싱 검증
- ✅ `test_reranker_v2_response_format`: JSON 응답 형식 검증
- ✅ `test_reranker_v2_multi_entity_guideline`: Multi-Entity 가이드라인 존재 확인
- ✅ `test_reranker_v2_name_mention_guideline`: Name Mentions 가이드라인 존재 확인
- ✅ `test_reranker_v2_self_verification_guideline`: Self-Verification 가이드라인 존재 확인
- ✅ `test_rerank_results_success`: v1 기본 동작 검증
- ✅ `test_rerank_results_with_v2_prompt`: v2 Feature Flag 작동 검증

### A/B Testing (Simulation Mode)
```bash
# v1 테스트
python3 scripts/compare_reranker_versions.py --version v1 --output /tmp/results_v1.json

# v2 테스트
python3 scripts/compare_reranker_versions.py --version v2 --output /tmp/results_v2.json

# 결과 비교
python3 scripts/compare_results.py /tmp/results_v1.json /tmp/results_v2.json
```

**시뮬레이션 결과:**
- Recall: v1 0.500 → v2 0.700 (✅ +40%)
- Precision: v1 0.800 → v2 0.780 (🟡 -2.5%)
- F1 Score: v1 0.615 → v2 0.738 (✅ +20%)
- **Decision**: ✅ ADOPT v2 (기준 충족: Recall +10%, Precision -5% 이내)

### Manual Verification (Scenarios)
> **⚠️ 프로덕션 적용 전 필수 확인**

1. **시나리오 1: Admin UI Playground 테스트**
   - "일론 머스크의 SpaceX와 Tesla 비교" 질문 입력
   - v1 vs v2 답변 품질 비교
   - → v2에서 SpaceX와 Tesla 모두 관련성 있게 평가되는지 확인

2. **시나리오 2: RAG Inspector 점수 확인**
   - RAG Inspector로 v1 vs v2 Reranker 점수 비교
   - Multi-Entity Query에서 점수 분포 차이 분석
   - → v2에서 Over-filtering 감소 확인

3. **시나리오 3: 실제 RAG API A/B 테스트**
   - `compare_reranker_versions.py`를 실제 RAG API에 연결
   - 10개 테스트 질문 실행 및 결과 분석
   - → 실제 Recall +10% 이상 달성 확인

## 📦 Files Changed

### 🆕 New Files
- `app/domain/services/prompts/reranker_v2.py`: Context-Aware Reranker v2 프롬프트
- `scripts/compare_reranker_versions.py`: A/B 테스트 실행 스크립트 (10개 테스트 질문, Recall/Precision 계산)
- `scripts/compare_results.py`: v1 vs v2 비교 및 의사결정 로직
- `tests/unit/domain/prompts/test_reranker_v2.py`: v2 프롬프트 검증 테스트 (6개)
- `specs/069-reranker-prompt-optimization/spec.md`: Spec 문서
- `specs/069-reranker-prompt-optimization/plan.md`: Implementation Plan
- `specs/069-reranker-prompt-optimization/task.md`: Task List
- `specs/069-reranker-prompt-optimization/walkthrough.md`: Walkthrough 문서
- `specs/069-reranker-prompt-optimization/pr_description.md`: PR Description

### 🛠 Modified Files
- `app/core/config.py` (+3): RERANKER_VERSION Feature Flag 추가
- `app/infrastructure/ai/rag_nodes.py` (+7, -1): Feature Flag 기반 버전 선택 로직 통합
- `.env.example` (+4): RERANKER_VERSION 설정 예시 추가
- `tests/unit/infrastructure/rag/test_rag_reranker.py` (+59): v2 Feature Flag Integration Test 추가

**Total:** 13 files changed (9 new, 4 modified)

## 🚀 Deployment Guide

### Step 1: v2 활성화
`.env` 파일 수정:
```bash
RERANKER_VERSION=v2  # v1에서 v2로 변경
```

### Step 2: Backend 재시작
```bash
docker-compose restart backend
# 또는
uv run uvicorn app.main:app --reload
```

### Step 3: 모니터링
- LangFuse Observability 대시보드 확인
- Rerank 점수 분포 변화 관찰
- 사용자 피드백 수집

### Rollback (필요 시)
문제 발생 시 즉시 롤백:
```bash
# .env 수정
RERANKER_VERSION=v1

# Backend 재시작
docker-compose restart backend
```

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과 (8/8 passed)
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [ ] Ruff lint 및 format 확인 완료 (PR 생성 전 실행 예정)
- [ ] Manual Testing 완료 (Task 4-2, 4-3)
- [ ] v2 채택 의사결정 완료 (Task 4-3)
- [ ] Production Deployment (Task 5, 의사결정 후)

## 📈 Expected Impact

### 정량적 개선
- Recall +10% 이상 (시뮬레이션 +40%)
- Multi-Entity Query 성능 향상
- Over-filtering 감소

### 정성적 개선
- 비교 질문 답변 품질 향상
- 다각적 정보 제공 가능
- 사용자 만족도 증대

## 🔗 Related

- [Spec 068: RAG System Architecture Review](file:///Users/ck/Project/doit/rag-ingestion/specs/068-rag-system-architecture-review/spec.md)
- [Spec 069](file:///Users/ck/Project/doit/rag-ingestion/specs/069-reranker-prompt-optimization/spec.md)
- [Implementation Plan](file:///Users/ck/Project/doit/rag-ingestion/specs/069-reranker-prompt-optimization/plan.md)
- [Walkthrough](file:///Users/ck/Project/doit/rag-ingestion/specs/069-reranker-prompt-optimization/walkthrough.md)

---

**Merge Condition**: Manual Testing (Task 4-2, 4-3) 완료 및 v2 채택 의사결정 후 Merge 가능
