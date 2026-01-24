# Spec-034: RAG Pipeline Recovery & Stability (Baseline 복구)

## 📋 배경 및 문제 정의 (Background & Problem)
Spec 033 리뷰 과정에서 특정 대상을 지목한 질문 시 검색 결과가 0건으로 나타나는 **Strict Filtering** 이슈와, 컨텍스트가 없음에도 LLM이 자의적으로 답변하는 **Hallucination** 위험이 발견되었습니다. 또한, `checkpoints.sqlite` 파일의 안정성 문제와 Playground 연동 미흡으로 인해 사용자 경험 및 시스템 신뢰도가 저하된 상태입니다.

이를 해결하기 위해 검색 실패 시 자동으로 범위를 확장하는 **Fallback 로직**을 구현하고, LLM의 답변 가드레일을 강화하며, 인프라스트럭처(Checkpointer)의 안정성을 확보하고자 합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **Filter Fallback (Graph Logic)**:
   - `retrieve_hybrid` 노드에서 필터링된 검색 결과가 0건일 경우, 자동으로 필터를 제거한 Global Search를 재수행하여 컨텍스트를 확보해야 함.
   - `RAGGraphState`에 fallback 발생 여부를 기록하여 투명성을 확보해야 함.
2. **Empty Guard (Prompting)**:
   - `generate_answer` 노드에서 컨텍스트가 부족하거나 없을 경우, 지적 재산권이나 내부 지식 기반이 아닌 "모른다" 또는 "정보가 부족하다"라고 명확히 답하도록 프롬프트 강화.
3. **Checkpointer & UI Stability (Infrastructure & Admin)**:
   - `checkpoints.sqlite` 파일 손상을 방지하고, 손상 시 복구하거나 재성성하는 방어 로직 검토.
   - Admin Dashboard(Playground)에서 LangGraph의 대화 내역(Thread)이 정상적으로 저장되고 로드되도록 `checkpointer` 주입 코드 수정.
   - **HITL Control 연동**: SqliteSaver 연동을 통해 Admin UI에서 중단된 상태를 조회하고 재개(Resume)할 수 있는 기능 연동 확인.
   - **Reasoning Trace Viewer**: Graph State에 저장된 사고 과정(State Trace)을 Playground의 디버그 창에서 시각화.

### Non-Functional Requirements
1. **State Traceability**: Fallback 발생 여부를 State에 남겨 디버깅 가능하게 함.
2. **Backward Compatibility**: 기존 RAGService 인터페이스와 호환성 유지.

### [Documentation Layer]
#### [MODIFY] `docs/architecture/rag_pipeline.md`
- "Troubleshooting & Lessons Learned" 섹션에 Spec 034 해결책(Fallback, Empty Guard) 추가.
#### [MODIFY] `docs/guides/admin_guide.md`
- Playground의 HITL Control 및 Reasoning Trace Viewer 사용 가이드 추가.
