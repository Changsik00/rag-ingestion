# Spec-029: Admin Agentic Workflow (LangGraph Integration)

## 📋 배경 및 문제 정의 (Background & Problem)
현재 Admin Dashboard의 채팅 인터페이스(`RAG_Playground`)는 사용자의 입력을 단순히 검색 쿼리로 처리하여 RAG 파이프라인(`RAGService.retrieve_and_generate`)을 호출하는 단순 구조입니다.
이로 인해 다음과 같은 한계가 존재합니다:
1.  **URL 수집 불가**: 사용자가 채팅창에 URL을 입력해도 이를 수집 요청으로 인식하지 못하고 검색 쿼리로 처리합니다.
2.  **도구 활용 부재**: Spec 028에서 구현한 Agentic 도구(`ingest_url`)를 Admin UI에서 직접 활용할 수 없습니다.

이를 해결하기 위해 LangGraph를 도입하여 사용자의 의도(수집 vs 검색)를 파악하고 적절한 도구로 라우팅하는 **Agentic Workflow**가 필요합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **Intent Routing**: 사용자 입력에 URL이 포함되어 있거나 명시적인 수집 요청이 있는 경우 `Ingest Tool`로, 일반 질문인 경우 `Search Tool`로 라우팅.
2.  **Tool Integration**:
    *   `ingest_url`: `IngestionService`를 사용하여 URL 수집 수행.
    *   `search_knowledge_base`: `RAGService`를 사용하여 지식 검색 수행.
3.  **UI Feedback**: Streamlit UI에서 도구 실행 상태(예: "수집 중...", "검색 중...")와 결과를 사용자에게 시각적으로 피드백.

### Non-Functional Requirements
1.  **Code Reusability**: Spec 028에서 구현한 `app/interfaces/mcp/server.py`의 핵심 로직이나 서비스를 최대한 재사용.
2.  **User Experience**: 긴 작업(수집) 실행 시 사용자가 멈춘 것으로 오해하지 않도록 진행 상태 표시.

## ✅ Definition of Done
1.  `4_RAG_Playground.py`에서 URL 입력 시 수집이 정상적으로 수행되고 결과가 표시됨.
2.  일반 질문 입력 시 기존과 동일하게 RAG 답변이 생성됨.
3.  LangGraph 구조(`AdminState`, `Router`, `Tools`)로 코드가 리팩토링됨.
4.  단위 테스트(Router 분류 로직) 통과.
