# Spec 069: Reranker Prompt Optimization

## 🎯 Summary

Reranker v2 Context-Aware 프롬프트 도입으로 Over-filtering 문제 해결 및 Recall 개선. Feature Flag 시스템으로 안전한 A/B 테스트 지원.

## 📋 Related Issues

- Spec 068: Root Cause #3 (Reranker PENALTY 규칙 Over-filtering)
- Backlog: Phase 8.1 - Quick Wins

## 🔧 Changes

### Core Implementation
- **Reranker v2 Prompt** (`app/domain/services/prompts/reranker_v2.py`)
  - PENALTY 규칙 제거
  - Context-Aware 평가 기준 추가 (Multi-Entity, Name Mentions, Self-Verification)
  
- **Feature Flag** (`app/core/config.py`, `.env.example`)
  - `RERANKER_VERSION` 추가 (v1/v2 선택 가능)
  
- **RAG Nodes 통합** (`app/infrastructure/ai/rag_nodes.py`)
  - Feature Flag 기반 버전 선택 로직

### Testing
- **Prompt Validation** (`tests/unit/domain/prompts/test_reranker_v2.py`)
  - 6 tests: 프롬프트 형식, JSON 파싱, 가이드라인 검증
  
- **Integration Test** (`tests/unit/infrastructure/rag/test_rag_reranker.py`)
  - 2 tests: v1 기본 동작, v2 Feature Flag 작동

### A/B Testing Infrastructure
- **Test Script** (`scripts/compare_reranker_versions.py`)
  - 10개 테스트 질문, Recall/Precision 계산
  
- **Comparison Script** (`scripts/compare_results.py`)
  - v1 vs v2 비교, 자동 의사결정 로직

## ✅ Verification

### Automated Tests
```bash
uv run pytest tests/unit/domain/prompts/test_reranker_v2.py
uv run pytest tests/unit/infrastructure/rag/test_rag_reranker.py
```
- **Result**: 8/8 passed ✅

### A/B Testing (Simulation Mode)
```bash
python3 scripts/compare_reranker_versions.py --version v1 --output /tmp/results_v1.json
python3 scripts/compare_reranker_versions.py --version v2 --output /tmp/results_v2.json
python3 scripts/compare_results.py /tmp/results_v1.json /tmp/results_v2.json
```

**Simulation Results**:
- Recall: v1 0.500 → v2 0.700 (✅ +40%)
- Precision: v1 0.800 → v2 0.780 (🟡 -2.5%)
- F1 Score: v1 0.615 → v2 0.738 (✅ +20%)
- **Decision**: ✅ ADOPT v2 (기준 충족)

### Manual Testing Checklist
> **⚠️ 프로덕션 적용 전 필수 확인**

- [ ] Admin UI Playground 테스트
  - [ ] "일론 머스크의 SpaceX와 Tesla 비교"
  - [ ] "Claude와 GPT-4의 차이점"
- [ ] RAG Inspector로 v1 vs v2 점수 비교
- [ ] 실제 RAG API로 A/B 테스트 실행
- [ ] LangFuse로 실제 Rerank 점수 분포 확인

## 🚀 Deployment

### Step 1: Enable v2
`.env` 파일 수정:
```bash
RERANKER_VERSION=v2
```

### Step 2: Restart Backend
```bash
docker-compose restart backend
```

### Step 3: Monitor
- LangFuse Observability 확인
- Rerank 점수 분포 변화 관찰
- 사용자 피드백 수집

### Rollback (필요 시)
```bash
# .env
RERANKER_VERSION=v1

# Restart
docker-compose restart backend
```

## 📊 Expected Impact

### Quantitative
- Recall +10% 이상 (시뮬레이션 +40%)
- Multi-Entity Query 성능 향상
- Over-filtering 감소

### Qualitative
- 비교 질문 답변 품질 향상
- 다각적 정보 제공 가능
- 사용자 만족도 증대

## 🔗 Related Docs

- [Spec](./spec.md)
- [Implementation Plan](./plan.md)
- [Task List](./task.md)
- [Walkthrough](./walkthrough.md)

## 📝 Commits

```
c90da32 docs(spec-069): update task.md - Task 4-1 automated tests passed
0d9af7d feat(spec-069): add reranker a/b testing scripts
17f41d1 test(spec-069): add reranker v2 integration test
06fb54c docs(spec-069): add RERANKER_VERSION to .env.example
7c03595 docs(spec-069): update task.md progress
20bf4cb feat(spec-069): integrate reranker v2 with feature flag
47d541f feat(spec-069): add reranker version feature flag
f9d95c7 test(spec-069): add reranker v2 prompt validation test
e90b126 feat(spec-069): add reranker v2 context-aware prompt
```

**Total**: 9 commits

## 👥 Reviewers

Please review:
1. Reranker v2 프롬프트 로직 (Context-Aware 기준 적절성)
2. Feature Flag 구현 (안전성, 확장성)
3. A/B Testing 스크립트 (테스트 케이스 충분성)
4. Manual Testing 결과 (실제 성능 검증)

---

**Merge Condition**: Manual Testing (Task 4-2, 4-3) 완료 후 Merge 가능
