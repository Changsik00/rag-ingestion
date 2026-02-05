# Walkthrough: Spec-064 RAG Observability

## 📋 Changes Implemented

### 1. LangFuse Integration (Infrastructure)
- **`langfuse` Dependency**: 프로젝트에 `langfuse` 패키지를 추가하여 Observability 추적 환경을 구성했습니다.
- **`LangfuseCallbackHandler` Helper**: `app/infrastructure/monitoring/langfuse_helper.py`를 통해 핸들러 생성을 캡슐화하고 안전한 초기화를 보장했습니다.

### 2. RAG Pipeline Service Layer
- **Callback Injection**: `RAG` 클래스(`rag.py`) 초기화 시 `LangfuseCallbackHandler`를 생성하여 LangGraph 실행 config에 주입했습니다.
- **Node Propagation**: `RAGNodes`(`rag_nodes.py`)의 `generate_answer` 및 `rerank_results` 메서드에서 LLM 호출 시 `config`를 전파하여 Trace가 끊기지 않도록 수정했습니다.
- **Trace ID Mapping**: `RAGResult` 객체에 `trace_id`와 `trace_url`을 포함시켜 UI로 전달할 수 있게 했습니다.

### 3. Admin UI Experience
- **Playground Link**: 답변 생성 완료 후 `LangFuse` Trace URL이 존재하면 "🔍 View Trace in LangFuse" 버튼을 렌더링하여 원클릭으로 상세 로그에 접근하도록 했습니다.

### 4. Documentation
- **Architecture Note**: `docs/features/observability.md`를 신규 작성하여 비동기 배치 전송(Push) 방식과 딥링크 아키텍처를 상세히 기록했습니다.

## 🧪 Verification Results

### 1. Automated Tests
- **Command:** `uv run pytest`
- **Result:** ✅ Passed (42 tests passed in 1.49s)
- **Note:** 기존 테스트 `test_rag_pipeline.py` 등이 수정된 `rag_nodes.py` 로직(config 인자 추가)과 호환되어 정상 작동함을 확인했습니다.

### 2. Manual Verification
(LangFuse API Key가 설정되지 않은 상태에서의 Graceful Fallback 검증)
1.  **Action:** Admin UI 실행 (`uv run streamlit run admin/Home.py`)
2.  **Action:** RAG Playground 질문 입력 ("테스트 질문")
3.  **Observation:**
    - 터미널에 `LangFuse environment variables not set. Skipping observability.` 로그 출력.
    - RAG 파이프라인이 에러 없이 정상 실행되고 답변 생성.
    - "View Trace" 버튼이 표시되지 않음 (Expected Behavior).
4.  **Verification**: LangFuse 설정이 없을 때 서비스가 죽지 않고 정상 동작함.

### 3. Evidence
- **Architecture Doc**: `docs/features/observability.md`
- **Helper Code**:
```python
# app/infrastructure/monitoring/langfuse_helper.py
def get_langfuse_handler(...):
    if not HAS_LANGFUSE: return None
    # ... checks env vars ...
    return LangfuseCallbackHandler(...)
```

## 🔍 Key Findings
- LangFuse의 `CallbackHandler` 방식은 기존 코드를 거의 수정하지 않고도(Invasive하지 않게) 강력한 Tracing을 제공합니다.
- 사용자 질문 의도였던 "실시간 상태 확인"은 기술적으로 무거운 Polling보다는 간결한 "사후 분석 링크 제공"으로 해결하는 것이 RAG 시스템 성능 유지에 유리함을 확인했습니다.
