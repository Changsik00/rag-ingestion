# Observability Architecture: LangFuse Integration

## 📋 Overview
이 문서는 **Spec 064: RAG Observability Dashboard**의 구현 상세와 통신 매커니즘을 설명합니다. RAG 파이프라인의 실행 과정을 추적(Tracing)하고, 성능 지표(Latency, Token Usage)를 수집하기 위해 **LangFuse**를 통합했습니다.

---

## 🏗️ Architecture Mechanism

### 1. Data Transmission: "Async HTTP Batch" (Push)
사용자 질문에 대해 "실시간 상태 확인"이 어떻게 이루어지는지에 대한 기술적 설명입니다.

> **💡 Key Concept**: Long Polling이나 SSE(Server-Sent Events)가 **아닙니다**.

LangFuse Python SDK는 **Fire-and-Forget** 방식의 **비동기 배치 전송**을 사용합니다.
1. **Local Buffering**: RAG 파이프라인 실행 중 이벤트(Start, End, Input, Output)가 발생하면, 즉시 서버로 보내지 않고 로컬 메모리 큐에 쌓습니다.
2. **Background Thread**: 별도의 백그라운드 스레드가 주기적으로(기본값 0.5초) 큐에 쌓인 이벤트를 묶어서(Batch) LangFuse 서버로 **HTTP POST** 요청을 보냅니다.
3. **Optimistic Trade-off**: 메인 RAG 로직은 이 과정을 기다리지 않으므로(Non-blocking), 사용자가 느끼는 응답 지연(Latency)은 0에 가깝습니다.

### 2. Deep Linking Concept
Admin UI에서는 실시간 스트리밍 데이터를 받아 그래프를 그리는 것이 아니라, 이미 생성된(또는 생성 중인) Trace의 **고유 URL(Trace ID)**을 생성하여 사용자에게 제공합니다.

---

## 📊 Sequence Diagram (Data Flow)

```mermaid
sequenceDiagram
    participant Admin as Admin UI (Streamlit)
    participant RAG as RAG Service
    participant LF_SDK as LangFuse SDK (Buffer)
    participant LF_Cloud as LangFuse Cloud

    Note over Admin, RAG: User asks a question
    Admin->>RAG: retrieve_and_generate(query)
    RAG->>LF_SDK: Initialize Trace (ID: abc-123)
    
    rect rgb(240, 248, 255)
        Note right of RAG: RAG Pipeline Execution
        RAG->>LF_SDK: 1. Intent Classification Start/End
        RAG->>LF_SDK: 2. Query Rewriting Start/End
        RAG->>LF_SDK: 3. Retrieval Start/End
        RAG->>LF_SDK: 4. Generation Start/End
    end

    parallel
        RAG-->>Admin: Return Response + trace_url
        LF_SDK->>LF_Cloud: Async HTTP POST (Batch Logs) [Background]
    end

    Note over Admin: "View Trace" Button appears
    Admin->>LF_Cloud: User clicks Link (Open in New Tab)
    LF_Cloud-->>Admin: Render Trace Timeline
```

---

## ❓ FAQ: Why not WebSocket/SSE?

**Q: 터미널 로그처럼 실시간으로 진행 상황을 UI에서 보고 싶습니다. 왜 WebSocket을 안 쓰나요?**

**A:**
1.  **목적의 차이**: Observability의 주 목적은 "사후 분석"과 "디버깅"입니다. 실행 중인 텍스트가 톡톡 튀어나오는 것(Token Streaming)은 Streamlit의 `write_stream`으로 이미 가능하지만, **내부 로직의 상세 데이터(Top-k score, 검색된 문서의 메타데이터, 토큰 비용 등)**는 너무 방대하여 실시간 UI에 모두 표시하기 부적합합니다.
2.  **구현 복잡도 vs 효율**: WebSocket을 통해 이 모든 메타데이터를 실시간으로 스트리밍하려면 백엔드(FastAPI)와 프론트엔드(Streamlit) 간에 복잡한 소켓 연결 관리가 필요합니다.
3.  **LangFuse의 강점**: LangFuse는 이러한 데이터를 전문적으로 시각화해주는 대시보드를 제공하므로, 우리는 데이터를 잘 "던져주기(Push)"만 하고, 상세 분석은 전문 도구(LangFuse UI)에 위임(Link)하는 것이 가장 효율적인 아키텍처입니다.
