# Spec 004: Async Processing & Task Status

## 1. 개요 (Overview)
현재의 동기식(Synchronous) 인제스션 API를 **비동기식(Asynchronous)**으로 전환하여, 대용량 처리 시의 타임아웃 문제를 해결하고 사용자 경험(UX)을 개선합니다.

## 2. 목표 (Goals)
1.  **Non-blocking API**: `/ingest/web` 요청 시 즉시 `Job ID`를 반환하고, 실제 작업은 백그라운드에서 수행합니다.
2.  **Task State Management**: 백그라운드 작업의 진행 상황(Pending -> Running -> Completed/Failed)을 실시간으로 추적 가능하게 합니다.
3.  **Stability**: 작업 실패 시에도 서버가 멈추지 않고, 에러 상태를 DB에 남겨야 합니다.

## 3. 상세 요구사항 (Requirements)

### 3.1 API 변경
-   **`POST /ingest/web`**
    -   **As-Is**: 수집 완료까지 대기 후 결과 반환 (Timeout 위험).
    -   **To-Be**: HTTP 202 Accepted 응답 + `job_id` 즉시 반환.
-   동작 흐름:
    1.  요청 수신 -> `IngestionJob` 생성 (Status: `PENDING`)
    2.  `BackgroundTasks`에 작업 등록
    3.  응답 반환 (202 Accepted)
    4.  (Background) Scrape -> Save -> Status Update (`COMPLETED`/`FAILED`)

### 3.2 도메인/서비스 로직
-   `IngestionService.ingest` 메서드는 이제 리턴값을 바로 주지 않아도 되며(Void), 내부에서 Job Status를 업데이트하는 책임을 집니다.
-   기존에 구현된 `JobRepository`를 적극 활용합니다.

### 3.3 테스트 요구사항
-   비동기 실행 여부 검증 (Mocking `BackgroundTasks`).
-   실패 시나리오에서 Job Status가 `FAILED`로 잘 업데이트되는지 검증.

## 4. 제약 사항 (Constraints)
-   Celery나 Redis Queue 같은 무거운 의존성 대신, FastAPI 내장 **`BackgroundTasks`**를 우선 사용합니다 (Phase 1).
-   이후 확장이 필요하면 Redis로 교체 가능한 구조를 유지합니다.
