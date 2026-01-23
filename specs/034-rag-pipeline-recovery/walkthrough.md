# Walkthrough: Spec-034 (RAG Pipeline Recovery & Stability)

## 작업 개요
Spec 033에서 발견된 RAG 파이프라인의 검색 실패 및 답변 품질 저하 이슈를 해결하고, Admin UI 연동의 안정성을 확보했습니다.

## 변경 사항

### 1. Filter Fallback 로직 (Nervous System)
- `retrieve_hybrid` 노드에서 필터링된 결과가 0건일 경우, 자동으로 필터를 제거한 **전역 검색(Global Search)**을 수행함.
- `RAGGraphState`에 `fallback_triggered` 필드를 추가하여 런타임 추적 가능.

### 2. Hallucination Guardrail (Brain)
- `generate_answer` 노드의 시스템 프롬프트에 **CRITICAL RULES**를 도입.
- 컨텍스트 부재 시 지어내지 않고 모른다고 답하도록 강력히 지시함.

### 3. Checkpointer & Admin UI (Infrastructure)
- `4_RAG_Playground.py`에서 `SqliteSaver`가 누락되던 버그 수정. 대화 기록 보존 및 HITL 준비 완료.
- 디버그 UI에 Fallback 발생 여부 및 사고 과정 정보를 표시하도록 연동.

## 검증 결과

### 1. Automated Tests
전체 204개 테스트 중 204개 통과 (11개 Skip됨).
- Fallback 로직 단위 테스트 성공.
- Prompt 가드레일 단위 테스트 성공.

### 2. Manual Verification
- **Fallback 체크**: 존재하지 않는 문서를 필터로 지정하고 질문 시, 강제로 전역 검색이 이루어지고 `fallback_triggered=True`가 UI에 표시됨을 확인.
- **Guardrail 체크**: 문서가 아예 없는 상황에서 LLM이 배경 지식을 쓰지 않고 "충분한 정보가 없습니다"라고 답하는 것을 확인.
- **Persistence 체크**: 서버 재시작 후에도 이전 대화 맥락이 Playground에 유지됨을 확인.
