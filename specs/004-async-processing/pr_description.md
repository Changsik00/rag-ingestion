# PR Description: Spec 004 Async Processing

## 📌 변경 사항 요약
인제스션 API(`.post /ingest/web`)를 **비동기 처리(Async Processing)** 방식으로 전환했습니다. 이제 긴 작업 시간으로 인한 타임아웃 없이 대량의 문서를 안정적으로 수집할 수 있습니다.

### 주요 변경점
1.  **API 응답 변경**: `POST /ingest/web` 요청 시 즉시 `202 Accepted`와 `job_id`를 반환합니다. (기존: 완료 시까지 대기 후 200 OK)
2.  **비동기 태스크**: FastAPI `BackgroundTasks`를 도입하여, 응답 반환 후 백그라운드에서 `Scrape -> Save -> Status Update` 파이프라인이 실행됩니다.
3.  **UseCase 리팩토링**: `IngestionService.ingest`를 `create_job`(동기)과 `process_job`(비동기)으로 분리하여 책임 범위를 명확히 했습니다.
4.  **테스트 보강**: 비동기 흐름 검증을 위한 통합 테스트(`test_async_ingest.py`)를 추가하고, 기존 Job 관련 테스트를 호환되도록 수정했습니다.

## ✅ 매뉴얼 검증 결과
- **Docker 환경 재기동**: `docker compose up --build backend` 완료.
- **API 테스트**:
    - `POST /ingest/web` -> `202 Accepted` 응답 확인.
    - `GET /jobs/{job_id}` -> `PENDING` -> `RUNNING` -> `COMPLETED` 상태 변화 확인.

## ⚠️ Breaking Changes
- 클라이언트는 더 이상 `POST /ingest/web`의 응답 본문에서 마크다운 결과를 바로 받을 수 없습니다.
- Job ID를 통해 상태를 조회하거나 대시보드를 확인해야 합니다.
