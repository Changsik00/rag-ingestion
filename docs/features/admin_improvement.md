# Admin & Backoffice 2.0 Improvement Plan

이 문서는 Admin/Backoffice 시스템의 사용성 개선, 가시성 확보, 그리고 장기적인 기술 스택 변화를 위한 계획을 정리합니다.

---

## 1. 개선 요구사항 (Requirements)

### 1.1 Verification Lab (Scripts to UI)
*   **현재**: `verify_llm.py`, `evaluate_rag_quality.py` 등을 터미널에서 실행해야 함.
*   **개선**: Admin UI에 **"Verification Lab"** 페이지를 추가하여, 클릭 한 번으로 테스트를 실행하고 결과를 표/그래프로 시각화.
    *   Input: Query, Top-K, Temperature 설정
    *   Output: LLM 응답, 검색된 청크, 소요 시간, 토큰 사용량 표시

### 1.2 Knowledge Graph Visualization
*   **Style**: 현재 Dark Mode에서 Edge(선)와 Text가 배경색과 비슷하여 안 보임.
    *   👉 **Action**: `agraph` 설정에 테마(CSS) 명시적 주입 및 색상 대비 개선.
*   **Usability**: Cypher Query Builder가 직관적이지 않음.
    *   👉 **Action**: 자주 쓰는 쿼리(Saved Queries) 콤보박스 제공, "Entity 클릭 시 이웃 노드 탐색" 기능 추가.
*   **Bug**: Preset 동작 불량 수정.

### 1.3 Observability (Debugging RAG)
*   **문제**: Streamlit은 Server-Side Framework이므로 브라우저 Concept의 Network 탭에서 내부 API 호출(RAG 로직)을 볼 수 없음.
*   **해결**:
    *   **Level 1 (UI)**: **"RAG Inspector"** 페이지 추가. 최근 요청의 `trace_id`를 조회하여 각 단계(Step)별 Input/Output/Latnecy를 타임라인으로 표시.
    *   **Level 2 (Tool)**: **LangSmith** 연동 (이미 되어 있다면 링크 제공).

### 1.4 User Feedback Loop
*   **문제**: UI에 좋아요/싫어요 버튼이 있지만 동작하지 않음.
*   **해결**: `on_click` 이벤트에 `POST /feedback` API 연결.
    *   싫어요 클릭 시 "이유(카테고리)" 선택 팝업 표출 (Hallucination, Outdated, Irrelevant).

### 1.5 Backoffice Features (Ideas)
*   **Job Monitor**: Ingestion 작업 상태 실시간 프로그레스 바 (WebSocket/Polling).
*   **Token Usage Dashboard**: 일별/모델별 토큰 비용 차트.
*   **Vector Space Visualizer**: `UMAP` 등을 사용하여 청크들의 군집도 시각화 (검색 품질 디버깅용).
*   **Prompt Playground**: System Prompt를 UI에서 수정하고 즉시 테스트 (A/B Test).

---

## 2. Tech Stack Analysis (Streamlit vs The World)

### 2.1 Streamlit (Current)
*   **장점**: Python만으로 빠르게 개발 가능. 데이터 시각화(Chart)에 강력함.
*   **단점**:
    *   **Customization**: 복잡한 인터랙션(예: 드래그 앤 드롭, 정밀한 CSS 제어) 불가.
    *   **Network Tab**: 클라이언트 사이드 디버깅 불가. (모든 게 서버에서 렌더링됨)
    *   **Performance**: 사용자가 늘어나면 느림 (매번 스크립트 재실행).

### 2.2 Benchmarking & Alternatives

| 후보 (Candidate) | 장점 (Pros) | 단점 (Cons) | 추천 상황 |
| :--- | :--- | :--- | :--- |
| **Next.js + React** | 무한한 자유도, 풍부한 에코시스템(ShadcnUI, Tremor), 클라이언트 디버깅 용이. | 개발 비용 높음 (Frontend/Backend 분리, JS/TS 숙련도 필요). | **상용 서비스**, 복잡한 UI가 필요할 때. |
| **Gradio 5** | Streamlit보다 빠름(SSR), ML 데모에 최적화됨. | 역시 Custom UI에는 한계가 있음. | 간단한 모델 데모. |
| **Reflex (Pure Python)** | Python으로 React 앱을 만듬. Streamlit보다 유연함. | 아직 성숙도 낮음, 버그 많음. | Python만 쓰고 싶지만 좀 더 App 같은 걸 원할 때. |

### 2.3 Recommendation
*   **단기 (Phase 6)**: Streamlit 유지 + **Custom Component** 활용으로 한계 극복.
*   **중장기 (Phase 7)**: **Next.js + ShadcnUI**로 전환. (Admin이 단순 대시보드를 넘어 "지식 관리 도구(CMS)"로 발전한다면 필수).

---

## 3. Action Plan (Backlog)

이 내용을 바탕으로 Backlog에 **Phase 7: Advanced Admin & Observability**를 신설합니다.

*   **Spec 070**: Admin UI UX/Style Upgrade (Graph, Feedback)
*   **Spec 071**: Verification Lab & Observability (Scripts to UI, Trace Viewer)
*   **Spec 072**: Tech Stack Migration Pilot (Next.js)
