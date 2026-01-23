# feat(spec-034): rag pipeline recovery and stability

## 📋 Summary
Spec 033 리뷰에서 발견된 RAG 파이프라인의 검색 실패(Strict Filtering)와 할루시네이션 위험을 해결했습니다. 검색 결과가 없을 때 자동으로 범위를 확장하는 Fallback 로직을 도입하고, LLM 답변 가드레일을 대폭 강화했습니다. 또한 Playground의 대화 유실 문제를 해결하고 디버그 정보를 가시화했습니다.

## 🎯 Key Review Points
1. **Filter Fallback 로직**: `retrieve_hybrid` 노드에서 필터링 결과가 0건일 때 자동으로 필터를 해제하고 전역 검색을 수행하여 컨텍스트를 확보합니다.
2. **LLM Prompt 강화**: 컨텍스트에 정보가 없을 경우 배경지식을 쓰지 않고 모른다고 답하도록 **CRITICAL RULES**를 추가했습니다.
3. **Admin UI 연동**: `SqliteSaver` 연동 수정으로 대화 내역이 보존되며, 디버그UI에서 Fallback 발생 여부와 사고 과정(Reasoning)을 확인할 수 있습니다.

## 🧪 Verification
### Automated Tests
```bash
# Fallback 및 Prompt 단위 테스트 실행
uv run pytest tests/unit/infrastructure/rag/test_rag_nodes.py -v

# 전체 통합 테스트 (204 passed)
uv run pytest -v
```

### Manual Verification
- **Fallback 시나리오**: 존재하지 않는 문서를 고정(Manual Filter)하고 질문 시, "🔄 Fallback Triggered" 경고가 뜨며 일반 검색 결과로 답변하는지 확인.
- **Hallucination 시나리오**: 관련 문서가 전혀 없을 때 LLM이 정보를 지어내지 않고 부족함을 시인하는지 확인.

## 📦 Files Changed

### 🆕 New Files
- `specs/034-rag-pipeline-recovery/spec.md`: 요구사항 정의서
- `specs/034-rag-pipeline-recovery/plan.md`: 실행 계획서
- `specs/034-rag-pipeline-recovery/task.md`: 태스크 작업 목록
- `specs/034-rag-pipeline-recovery/walkthrough.md`: 작업 결과 기술서

### 🛠 Modified Files
- `app/infrastructure/rag/nodes.py` (+29, -5): Fallback 로직 및 프롬프트 강화
- `app/admin/pages/4_RAG_Playground.py` (+15, -1): Checkpointer 주입 및 디버그 UI 개선
- `app/domain/rag/state.py` (+3, -0): State에 fallback_triggered 필드 추가
- `docs/architecture/rag_pipeline.md` (+12, -5): 해결된 이슈 문서화
- `docs/guides/admin_guide.md` (+6, -0): Playground 사용 가이드 추가
- `tests/unit/infrastructure/rag/test_rag_nodes.py` (+119, -0): Fallback 및 Prompt 테스트 추가

**Total:** 9 files changed

## ✅ Definition of Done
- [x] 필터 검색 실패 시 자동 Fallback 및 시각화 확인
- [x] Empty Context 상황에서 할루시네이션 방지 프롬프트 작동 확인
- [x] Playground 대화 내역(Session) 보존 확인
- [x] 전체 린트 및 통합 테스트(204개) 통과
