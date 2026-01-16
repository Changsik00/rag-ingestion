# PR Description: Spec 004 Async Processing

## 📌 변경 사항 요약
인제스션 API(`.post /ingest/web`)를 **비동기 처리(Async Processing)** 방식으로 전환했습니다. 이제 긴 작업 시간으로 인한 타임아웃 없이 대량의 문서를 안정적으로 수집할 수 있습니다.

### 주요 변경점
1.  **API 응답 변경**: `POST /ingest/web` 요청 시 즉시 `202 Accepted`와 `job_id`를 반환합니다. (기존: 완료 시까지 대기 후 200 OK)
2.  **비동기 태스크**: FastAPI `BackgroundTasks`를 도입하여, 응답 반환 후 백그라운드에서 `Scrape -> Save -> Status Update` 파이프라인이 실행됩니다.
3.  **UseCase 리팩토링**: `IngestionService.ingest`를 `create_job`(동기)과 `process_job`(비동기)으로 분리하여 책임 범위를 명확히 했습니다.
4.  **테스트 보강**: 비동기 흐름 검증을 위한 통합 테스트(`test_async_ingest.py`)를 추가하고, 기존 Job 관련 테스트를 호환되도록 수정했습니다.

## 🛠️ Code Level Explanation (Implementation Details)

이번 작업의 핵심은 **"동기(Sync) 대기 구조"**를 **"비동기(Async) 접수 구조"**로 전환하는 것입니다.

### 1. API 계층: "접수처"의 변화 (`main.py`)
클라이언트가 요청을 보냈을 때 서버가 작업을 완료할 때까지 붙잡고 있는 것이 아니라, **"접수증(Job ID/202)"만 발급하고 즉시 응답**하는 패턴(Fire-and-Forget)을 적용했습니다.

```python
# [Before] 동기 방식: 모든 작업이 끝날 때까지 블로킹 (Timeout 위험 높음)
# @app.post("/ingest/web")
# async def ingest(...):
#     result = service.ingest(url)  # <--- 여기서 수십 초~수 분 소요 가능
#     return result

# [After] 비동기 방식: 접수증만 끊어주고 즉시 반환
@app.post("/ingest/web", status_code=status.HTTP_202_ACCEPTED)
async def ingest_web_page(
    request: IngestRequest,
    background_tasks: BackgroundTasks,  # <--- FastAPI Built-in Background Tasks
    service: IngestionService
):
    # 1. 접수증 생성 (DB에 'PENDING' 상태로 기록 - 매우 빠름)
    job = service.create_job(str(request.url))
    
    # 2. 백그라운드 작업 예약
    #    "이 job_id로 처리를 시작하세요"라고 태스크 큐에 등록
    background_tasks.add_task(service.process_job, job.job_id)
    
    # 3. 클라이언트에게 Job ID 반환하고 연결 종료
    return {"job_id": job.job_id, "status": job.status}
```

### 2. 비즈니스 로직: 책임의 분리 (`ingestion.py`)
기존의 단일 메서드(`ingest`)를 성격이 다른 두 가지 역할로 분리했습니다.

#### A. 접수 담당 (`create_job`)
- **역할**: 빠른 응답을 위한 경량 작업
- **동작**: `IngestionJob` 엔티티를 생성하고 `PENDING` 상태로 DB에 저장합니다.

#### B. 처리 담당 (`process_job`)
- **역할**: 실제 데이터를 다루는 무거운 작업 (CPU/IO Bound)
- **동작**:
    1.  Job 상태를 `RUNNING`으로 변경
    2.  `Scraper`를 통한 웹 수집 및 파싱
    3.  `DocumentRepository`를 통한 결과 저장
    4.  성공 시 `COMPLETED`, 실패 시 `FAILED`로 상태 최종 업데이트
- **안정성**: `try-except` 블록으로 감싸져 있어, 작업 중 에러가 발생해도 서버가 중단되지 않고 DB에 에러 로그를 남깁니다.

---

## ✅ 매뉴얼 검증 결과
- **Docker 환경 재기동**: `docker compose up --build backend` 완료.
- **API 테스트**:
    - `POST /ingest/web` -> `202 Accepted` 응답 확인.
    - `GET /jobs/{job_id}` -> `PENDING` -> `RUNNING` -> `COMPLETED` 상태 변화 확인.

## ⚠️ Breaking Changes
- 클라이언트는 더 이상 `POST /ingest/web`의 응답 본문에서 마크다운 결과를 바로 받을 수 없습니다.
- Job ID를 통해 상태를 조회하거나 대시보드를 확인해야 합니다.
