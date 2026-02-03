# Spec-055: RAG Precision & Advanced Settings

## 📋 배경 및 문제 정의 (Background & Problem)

### 현재 상황
현재 RAG Playground는 단순히 메시지를 전송하고 답변을 받는 기본적인 Chat UI만 제공합니다. 검색 품질에 영향을 미치는 핵심 파라미터(Top-K, Temperature, 검색 전략)는 백엔드 내부/환경변수에 하드코딩되어 있습니다.

### 문제점
*   **디버깅 어려움**: 답변이 이상할 때, retrieval 단계의 문제인지 generation 단계의 문제인지 파악하기 어렵습니다. 단순히 검색 갯수만 늘려도 해결될 문제를 코드 수정 없이는 테스트할 수 없습니다.
*   **유연성 부족**: 질문 유형(단답형 팩트 vs 창의적 아이디어)에 따라 다른 검색/생성 전략이 필요하지만, 일괄적인 설정값만 적용됩니다.
*   **API 명세 미흡**: `ask_agent` 엔드포인트가 `dict` 타입을 직접 받고 있어, 입력값에 대한 검증과 명세가 불명확합니다 (Spec 053 잔여 과제).

### 해결 방안
1.  **API DTO 강화**: `ChatRequest` DTO를 정의하여 `advanced_settings` 필드를 명시적으로 받도록 구조화합니다.
2.  **UI 고도화**: Admin Dashboard에 "Advanced Settings" 패널을 추가하여 사용자가 실시간으로 파라미터를 튜닝할 수 있게 합니다.
3.  **검색 전략 노출**: Vector only, Keyword only, Hybrid 등 검색 전략을 선택할 수 있는 옵션을 제공합니다.

## 📊 개념도 (Conceptual Architecture)
```mermaid
graph TD
    User[User / Admin] -->|Adjust Settings| UI[Streamlit Playground]
    UI -->|API Request with ChatRequest DTO| API[FastAPI Endpoint]
    API -->|Validation| Agent[ConversationalRAGAgent]
    Agent -->|Execute with Config| Graph[LangGraph Workflow]
    Graph -->|Retrieve with Top-K/Strategy| Retriever[Neo4j/Chroma Retriever]
    Graph -->|Generate with Temp| LLM[LLM Generator]
    
    subgraph ChatRequest DTO
        message: str
        filters: dict
        hitl_enabled: bool
        advanced_settings: AdvancedSettings
    end
    
    subgraph AdvancedSettings
        top_k: int
        temperature: float
        search_strategy: str
    end
```

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **API Update**: `POST /sessions/{id}/ask` 엔드포인트는 `ChatRequest` DTO를 통해 입력을 받아야 합니다.
2.  **DTO Definition**: `AdvancedSettings` 및 `ChatRequest` Pydantic 모델을 정의해야 합니다.
3.  **UI Control**: Playground 사이드바 또는 메인 화면에 Expander 형태로 다음 제어 기능을 제공해야 합니다.
    *   Top-K (Slider, 1~20)
    *   Temperature (Slider, 0.0~1.0)
    *   Search Strategy (Radio/Selectbox: Hybrid, Vector, Keyword)
4.  **Backend Logic**: 전달받은 파라미터가 실제 Retrieval 및 LLM 호출 시 동적으로 적용되어야 합니다.

### Non-Functional Requirements
1.  **Default Values**: 사용자가 설정을 건드리지 않았을 때를 위한 합리적인 기본값(Default)이 존재해야 합니다.
2.  **Backward Compatibility**: 기존 클라이언트가 `advanced_settings` 없이 요청해도 정상 동작해야 합니다.

## ✅ Definition of Done
1.  Admin Dashboard에서 파라미터를 변경하여 질문했을 때, 검색 결과 갯수나 답변 다양성이 변화하는 것을 육안으로 확인할 수 있다.
2.  Swagger UI에서 `ChatRequest` 스키마가 명확히 표시된다.
3.  통합 테스트(Integration Test)를 통해 파라미터 전달 흐름이 검증된다.
