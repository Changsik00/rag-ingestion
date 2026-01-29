# Implementation Plan: Spec-034 (RAG Pipeline Recovery)

## 📋 Branch Strategy
- `feature/034-rag-pipeline-recovery`

## 🛑 User Review Required
- [x] **Prompt Guardrail**: 현재 프롬프트에 "컨텍스트에 정보가 없으면 모른다고 답하라"는 지시를 한글/영문 중 어느 쪽으로 강화할지 결정 (일단 영문 지시문 추가 예정).
- [x] **Fallback 대상**: 필터 결과가 0건일 때 무조건 Fallback할지, 아니면 사용자에게 의사를 물어야 할지 (일단 자동 Fallback으로 구현).

## 🎯 Core Strategy
1. **State Traceability**: `RAGGraphState`에 `fallback_triggered` 필드를 추가하여 런타임 중 Fallback 발생 사실을 기록하고 이를 UI에 전달합니다.
2. **Fallback Mechanism**: `retrieve_hybrid` 노드에서 `final_filters`가 적용되었음에도 불구하고 검색 결과가 0건인 경우, `final_filters`를 리셋하고 병렬 검색을 재수행합니다.
3. **Hallucination Prevention**: `generate_answer` 노드의 시스템 지시문에 강력한 Negative Constraint를 추가합니다. (e.g., "If the provided context does not contain sufficient information, explicitly state that you don't know.")
4. **Admin UI Empowerment**: `SqliteSaver`가 정상화됨에 따라, 이전에 구현되었으나 연동되지 않았던 HITL Control(인터럽트 제어) 및 Reasoning Trace(사고 과정 추적) UI를 Playground와 완벽히 결합합니다.

## 📂 Proposed Changes

### [Domain Layer]
#### [MODIFY] `app/domain/rag/state.py`
- `fallback_triggered: bool` (Optional) 필드 추가.

### [Infrastructure Layer]
#### [MODIFY] `app/infrastructure/rag/nodes.py`
- `retrieve_hybrid`: 재시도 로직 추가.
- `generate_answer`: 프롬프트 템플릿 강화.

#### [MODIFY] `app/interfaces/api/dependencies.py`
- Playground 및 API에서 일관된 Checkpointer 주입을 위해 의존성 함수 정비.

#### [MODIFY] `app/admin/pages/4_RAG_Playground.py`
- `get_deps()` 내에서 `get_checkpointer()` 의존성을 사용하여 Graph 빌드 시 주입.
- State에 기록된 `fallback_triggered` 및 Reasoning 정보를 디버그 창에 표시하는 로직 추가.
- **HITL 지원**: `thread_id` 고정 및 Interrupt 발생 시 'Resume' 버튼 노출 로직 추가.

### [Infrastructure Layer]
#### [MODIFY] `app/infrastructure/rag/graph.py`
- `build()` 메서드에 `interrupt_before` 파라미터 추가하여 런타임 인터럽트 지원.

#### [MODIFY] `app/domain/rag/state.py`
- `reasoning_log: list[str]` 필드 추가하여 각 노드의 사고 과정을 추적.

### [Documentation Layer]
#### [MODIFY] `docs/architecture/rag_pipeline.md`
- "Troubleshooting & Lessons Learned" 섹션의 이슈들을 해결됨으로 업데이트하고 로직 설명 추가.
#### [MODIFY] `docs/guides/admin_guide.md`
- 새로운 디버그 UI 및 HITL 제어 기능에 대한 스크린샷 가이드(텍스트) 추가.

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests (Fallback 검증)
uv run pytest tests/unit/infrastructure/rag/test_rag_nodes.py

# Integration Tests (Checkpointer 검증)
uv run pytest tests/integration/bdd/test_rag_graph_flow.py
```

### Manual Verification
1. **Strict Filter 시나리오**: Playground에서 실제 DB에 없는 타겟(예: '존재하지 않는 인물')을 텍스트 필터로 걸고 질문 시, Fallback이 발생하여 일반 검색 결과가 나오는지 확인.
2. **Hallucination 체크**: 아무런 문서가 없는 상태에서 질문 시, 답변이 "정보가 없습니다" 계열로 나오는지 확인.
3. **Persistence 체크**: Playground 대화 후 Streamlit 재시작 시 대화 내역이 남아있는지 확인.
