# Spec-024: Advanced Admin Dashboard (Observability & HITL)

## 📋 배경 및 문제 정의 (Background & Problem)
현재 시스템은 API 및 테스트 코드를 통한 기능 검증에 의존하고 있어, 실제 데이터의 연결 구조나 지능형 에이전트의 사고 과정(Reasoning Flow)을 직관적으로 확인하기 어렵습니다. 또한 Human-in-the-loop(HITL) 기능이 구현되었으나, 이를 제어할 UI가 없어 API 호출로만 개입이 가능한 상태입니다. 이를 해결하기 위해 종합적인 관리자 대시보드가 필요합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **Graph Explorer**:
    - Neo4j 지식 그래프 시각화 (Interactive).
    - **Query Helper**: 초보자를 위한 '자주 쓰는 쿼리(Preset)' 및 '쿼리 빌더(Drop-down Builder)' 제공.
2. **HITL Control Center**:
    - `interrupt` 상태 조회 및 Resume/Update 제어.
    - **Live Status**: "생각 중...", "검색 중..." 등 현재 에이전트의 상태(Status)를 직관적으로 표시.
3. **Reasoning Trace Viewer**:
    - LangGraph 실행 트레이스 및 실패 원인 시각화.
4. **RAG Playground**:
    - 질의응답 테스트 및 Retriever 성능 검증.
    - **Feedback**: 사용자가 답변에 대해 좋아요/싫어요(Thumbs up/down) 피드백 가능.

### Non-Functional Requirements
1. **Interactive UI**: 정적인 테이블이 아닌 상호작용 가능한 UI (Streamlit) 제공.
2. **Real-time**: DB 및 Graph State의 변경 사항이 즉시 반영되어야 합니다.

## ✅ Definition of Done
1. Graph Explorer 페이지에서 노드 탐색 가능
2. HITL 페이지에서 멈춘 작업 Resume 가능
3. Trace Viewer에서 에러 로그 및 State 변화 확인 가능
4. Playground에서 질문-답변 테스트 가능
