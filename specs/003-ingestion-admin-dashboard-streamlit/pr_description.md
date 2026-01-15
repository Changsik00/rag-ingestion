# 🚀 Spec 003: Ingestion Admin Dashboard (Streamlit)

## 📝 Summary
This PR implements **Spec 003**, introducing a comprehensive Admin Dashboard to monitor and manage ingestion jobs. It includes the complete backend logic for job tracking (Status, History) and a Streamlit-based frontend for real-time monitoring and manual retries.

## 🔍 Key Review Points
*   **Backend (Job Tracking)**:
    *   `app/domain/entities/job.py`: `IngestionJob` entity and `JobStatus` enum.
    *   `app/domain/interfaces/job_repository.py`: Repository interface definition.
    *   `app/infrastructure/storage/neo4j_job_repo.py`: Neo4j implementation of the repository.
    *   `app/use_cases/ingestion.py`: Updated to trace job status (PENDING -> COMPLETED/FAILED).
*   **API Layer**:
    *   `app/interfaces/api/endpoints/jobs.py`: New endpoints (`GET /jobs`, `POST /retry`).
    *   `app/interfaces/api/dependencies.py`: Refactored dependency injection for cleaner architecture.
*   **Frontend (Streamlit)**:
    *   `app/admin/dashboard.py`: Dashboard UI logic (KPIs, Job List, Retry Action).
    *   `docker-compose.yml`: Added `streamlit` service configuration.

## 🛠 Verification Plan

### Automated Verification
Run the integration test suite to verify API endpoints and DB interactions:
```bash
uv run pytest tests/integration/test_jobs.py tests/integration/test_api_ingest.py
```

### Manual Verification
1.  **Start Services**:
    ```bash
    docker compose up --build
    ```
2.  **Access Dashboard**: Open [http://localhost:8501](http://localhost:8501).
3.  **Trigger Job**:
    ```bash
    curl -X POST "http://localhost:8000/ingest/web" -H "Content-Type: application/json" -d '{"url":"https://example.com"}'
    ```
4.  **Monitor**: Verify the new job appears in the Dashboard with `COMPLETED` status.
5.  **Test Retry**:
    - Manually trigger a failure (or mock it).
    - Click "Retry" button on the Dashboard for a failed job.
    - Verify status updates to `RUNNING` -> `COMPLETED`.

## 💻 Tech Stack
- **Backend**: FastAPI, Neo4j, Pydantic
- **Frontend**: Streamlit, Pandas
- **Infrastructure**: Docker Compose
