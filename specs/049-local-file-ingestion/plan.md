# Implementation Plan: Spec-049 Local File Ingestion

## 📋 Branch Strategy
- `feature/049-local-file-ingestion`

## 🛑 User Review Required
> [!IMPORTANT]
> - **AttributeError (APIClient.upload_file)**: Streamlit의 `@st.cache_resource`로 인해 이전 버전의 `APIClient` 인스턴스가 메모리에 남아 있을 가능성이 높습니다. 임시로 캐시를 제거하거나 리프레시를 유도하여 해결하겠습니다.

## 🎯 Core Strategy

### Architecture Context
```mermaid
sequenceDiagram
    participant User as Admin UI (Streamlit)
    participant API as FastAPI Backend
    participant Ingest as IngestionService
    participant Parser as FileProcessor
    participant DB as Vector/Graph DB

    User->>API: POST /ingest/file (Multipart)
    API->>Ingest: start_file_ingestion(file_content, filename)
    Ingest-->>API: Job ID (Async)
    API-->>User: 202 Accepted (Job ID)
    Ingest->>Parser: extract_text(binary_data, ext)
    Parser->>Ingest: Standardized Markdown
    Ingest->>DB: Save Chunks & Entities
    Note right of DB: Finalized Knowledge
```

| Component | Strategy | Reasoning |
|:---:|:---|:---|
| **API Interface** | `List[UploadFile]` | 다중 파일 멀티파트 업로드 지원 |
| **Admin UI** | `st.file_uploader(accept_multiple_files=True)` | 드래그 앤 드롭 및 다중 선택 UI 제공 |
| **Ingestion** | Batch Job Queue | 각 파일에 대해 개별 백그라운드 태스크 할당 |

## 📂 Proposed Changes

### [Backend/Core]

#### [MODIFY] `admin/utils/api_client.py`
- `@st.cache_resource` 데코레이터를 제거하여 매번 새로운 인스턴스를 생성하도록 하고, 캐싱 문제를 원천 차단합니다.

### [Frontend/Admin]

#### [MODIFY] `admin/pages/1_Ingestion_Management.py`
- 파일 업로드 위젯 및 처리 로직 추가.

#### [MODIFY] `admin/pages/4_RAG_Playground.py`
- 대화창 하단 혹은 사이드바에 즉석 파일 업로드 기능 추가.

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests: 파일 파싱 로직 검증
uv run pytest tests/unit/test_file_processor.py

# Integration Tests: 업로드 -> 인제스션 -> 검색 흐름 검증
uv run pytest tests/integration/test_file_ingestion_flow.py
```

### Manual Verification
1. **Admin UI**: 샘플 PDF 파일을 업로드하고 Job 상태가 `SUCCESS`로 변하는지 확인.
2. **Playground**: 업로드한 파일 내용에 대해 질문하고 정확한 출처와 함께 답변이 생성되는지 확인.
3. **API**: `curl` 명령어로 멀티파트 업로드 시 정상적으로 `Job ID`가 반환되는지 확인.
