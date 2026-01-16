# 🚀 Spec 003: Ingestion Admin Dashboard (Streamlit)

## 📝 요약 (Summary)
이 PR은 **Spec 003**을 구현하여, Ingestion 작업을 모니터링하고 관리할 수 있는 Admin Dashboard를 도입합니다. Ingestion 작업 상태 추적(Status, History)을 위한 백엔드 로직과 실시간 모니터링 및 수동 재시도(Retry)를 위한 Streamlit 기반 프론트엔드를 포함합니다.

## 🔍 주요 리뷰 포인트 (Key Review Points)
*   **Backend (Job Tracking)**:
    *   `app/domain/entities/job.py`: `IngestionJob` 엔티티 및 `JobStatus` Enum 정의.
    *   `app/domain/interfaces/job_repository.py`: Repository 인터페이스 정의.
    *   `app/infrastructure/storage/neo4j_job_repo.py`: Neo4j 기반 Repository 구현.
    *   `app/use_cases/ingestion.py`: 작업 상태 추적 로직 추가 (PENDING -> COMPLETED/FAILED).
*   **API Layer**:
    *   `app/interfaces/api/endpoints/jobs.py`: 신규 엔드포인트 추가 (`GET /jobs`, `POST /retry`).
    *   `app/interfaces/api/dependencies.py`: 의존성 주입(Dependency Injection) 구조 개선.
*   **Frontend (Streamlit)**:
    *   `app/admin/dashboard.py`: 대시보드 UI 로직 (KPI, 작업 목록, 재시도 액션).
    *   `docker-compose.yml`: `streamlit` 서비스 설정 추가.

## 🛠 검증 계획 (Verification Plan)

### 자동화 테스트 (Automated Verification)
Integration 테스트를 실행하여 API 엔드포인트 및 DB 상호작용을 검증합니다:
```bash
uv run pytest tests/integration/test_jobs.py tests/integration/test_api_ingest.py
```

### 수동 검증 (Manual Verification)
1.  **서비스 실행**:
    ```bash
    docker compose up --build
    ```
2.  **대시보드 접속**: 브라우저에서 [http://localhost:8501](http://localhost:8501) 접속.
3.  **작업 트리거**:
    ```bash
    curl -X POST "http://localhost:8000/ingest/web" -H "Content-Type: application/json" -d '{"url":"https://example.com"}'
    ```
4.  **모니터링**: 대시보드 목록에 해당 작업이 `COMPLETED` 상태로 나타나는지 확인.
5.  **재시도 테스트**:
    - (임의로 실패 상황을 만들거나) 실패한 작업에 대해 대시보드의 "Retry" 버튼 클릭.
    - 상태가 `RUNNING` -> `COMPLETED`로 변경되는지 확인.

## 💻 기술 스택 (Tech Stack)
- **Backend**: FastAPI, Neo4j, Pydantic
- **Frontend**: Streamlit, Pandas
- **Infrastructure**: Docker Compose
