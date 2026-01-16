# Implementation Plan - Spec 004

## User Review Required
> [!IMPORTANT]
> - `/ingest/web` API가 더 이상 `IngestResponse`(마크다운 본문)를 반환하지 않고, `job_id`만 반환합니다.
> - 클라이언트는 결과를 보려면 `GET /jobs/{job_id}`를 폴링하거나 대시보드를 확인해야 합니다.

## Proposed Changes

### App Layer
#### [MODIFY] [main.py](file:///Users/ck/Project/doit/rag-ingestion/app/interfaces/api/main.py)
- `POST /ingest/web`:
    - `BackgroundTasks` 파라미터 추가
    - `service.ingest` 호출을 background task로 등록
    - Return `202 Accepted` with `{"job_id": "...", "status": "PENDING"}`

### UseCase Layer
#### [MODIFY] [ingestion.py](file:///Users/ck/Project/doit/rag-ingestion/app/use_cases/ingestion.py)
- `ingest` 메서드:
    - Return type 변경: `IngestResponse` -> `None` (or `str` job_id for internal use)
    - `try/except` 블록 내에서:
        - Scraping 성공 시: `JobStatus.COMPLETED` 및 결과 DB 저장
        - 실패 시: `JobStatus.FAILED` 및 에러 메시지 저장

### Tests
#### [NEW] [test_async_ingest.py](file:///Users/ck/Project/doit/rag-ingestion/tests/integration/test_async_ingest.py)
- `POST /ingest/web` 요청 시 즉시 응답 오는지 확인
- Mock Service를 통해 백그라운드 태스크가 트리거되는지 확인

## Verification Plan

### Automated Tests
```bash
uv run pytest tests/integration/test_async_ingest.py
```

### Manual Verification
1. `docker compose up`
2. Swagger UI (`/docs`)에서 `/ingest/web` 호출
3. 즉시 응답(`202`) 확인
4. 대시보드(`8501`)에서 Job이 `PENDING` -> `RUNNING` -> `COMPLETED`로 변하는지 확인
