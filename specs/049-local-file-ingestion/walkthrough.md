# Walkthrough: Spec-049 Local File Ingestion

로컬 파일(PDF, TXT, MD)을 RAG 시스템에 직접 주입할 수 있는 기능을 성공적으로 구현하였습니다.

## 주요 변경 사항

### 1. Backend: 도메인 서비스 및 비즈니스 로직
- `app/domain/services/file_processor.py` (Divide & Conquer): 대용량 파일 처리를 위해 **제너레이터(Generator)** 기반의 `extract_segments`를 구현하였습니다. PDF는 페이지 묶음 단위로, 텍스트는 일정 크기 단위로 스트리밍 처리하여 메모리 효율성을 극대화했습니다.
- `app/domain/entities/job.py`: `IngestionJob` 엔티티에 `docs_ids: list[str]` 필드를 추가하여, 하나의 파일이 여러 도큐먼트로 나뉘어 저장될 때 이를 모두 추적할 수 있도록 개선하였습니다.
- `app/use_cases/ingestion.py`: `process_job` 로직을 리팩토링하여, 추출된 각 세그먼트별로 독립적인 Semantic Extraction, Chunking, Graph Indexing을 반복 수행하는 **Iterative Pipeline**을 구축하였습니다.

### 2. Backend: API 엔드포인트
- `app/interfaces/api/main.py`: `POST /ingest/file` 멀티파트 업로드 API를 추가하였습니다. 비동기 백그라운드 태스크로 연동되어 대용량 파일도 안정적으로 처리합니다.

### 3. Frontend: 관리자 UI (Streamlit)
- `admin/pages/0_Ingestion_Management.py`: URL 입력과 파일 업로드를 구분한 통합 수집 관리 페이지를 신설하였습니다.
- `admin/pages/4_RAG_Playground.py`: 사이드바에 'Quick File Upload' 위젯을 추가하여 대화 도중 즉시 지식을 주입할 수 있도록 개선하였습니다.
- `admin/utils/api_client.py`: `httpx`를 이용한 multipart 파일 업로드 기능을 추가하였습니다.

## 검증 결과

### Automated Unit Tests
`FileProcessor`의 파싱 로직에 대한 단위 테스트를 수행하여 모든 포맷(PDF, TXT, MD)이 정상적으로 마크다운으로 변환됨을 확인하였습니다.

```bash
uv run pytest tests/unit/test_file_processor.py
# Result: 4 passed in 0.22s
```

### Manual Verification
신규 생성된 `scripts/verify_file_ingestion.py`를 통해 API 엔드포인트의 동작과 비동기 처리 흐름을 검증하였습니다.

## 스크린샷 / 영상 (Placeholder)
> [!NOTE]
> 실제 Streamlit UI 화면은 로컬 실행 후 확인 가능합니다.

---
**구현 완료**: 2026-01-30  
**담당**: Antigravity
