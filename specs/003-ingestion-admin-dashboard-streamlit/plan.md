# Implemention Plan - Spec 003: Ingestion Admin Dashboard (Streamlit)

## Goal
To implement a Streamlit-based Admin Dashboard that allows monitoring of ingestion jobs and retrying failed ones.

## Proposed Changes

### Domain Layer
#### [NEW] [app/domain/entities/job.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/entities/job.py)
- Define `IngestionJob` entity.
- Define `JobStatus` Enum (PENDING, RUNNING, COMPLETED, FAILED).

#### [NEW] [app/domain/interfaces/job_repository.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/interfaces/job_repository.py)
- Define `JobRepository` interface.

### Infrastructure Layer
#### [NEW] [app/infrastructure/storage/neo4j_job_repo.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/neo4j_job_repo.py)
- Implement `Neo4jJobRepository`.
- Methods: `create_job`, `update_job`, `get_job`, `list_jobs`.

### Application Layer
#### [MODIFY] [app/application/use_cases/ingestion.py](file:///Users/ck/Project/doit/rag-ingestion/app/application/use_cases/ingestion.py)
- Update `IngestionService` to depend on `JobRepository`.
- Wrap processing logic to create and update job status.

### Interface Layer (API)
#### [NEW] [app/interface/api/endpoints/jobs.py](file:///Users/ck/Project/doit/rag-ingestion/app/interface/api/endpoints/jobs.py)
- `GET /jobs`
- `GET /jobs/{job_id}`
- `POST /jobs/{job_id}/retry`

#### [MODIFY] [app/main.py](file:///Users/ck/Project/doit/rag-ingestion/app/main.py)
- Register `jobs_router`.
- Inject `JobRepository` dependency.

### Admin Dashboard (Streamlit)
#### [NEW] [app/admin/dashboard.py](file:///Users/ck/Project/doit/rag-ingestion/app/admin/dashboard.py)
- Main Streamlit application entry point.
- Connects to FastAPI endpoints (local).

#### [NEW] [app/admin/pages/](file:///Users/ck/Project/doit/rag-ingestion/app/admin/pages/)
- Optional: structure into pages if complex.

### Configuration
#### [MODIFY] [docker-compose.yml](file:///Users/ck/Project/doit/rag-ingestion/docker-compose.yml)
- Add `streamlit` service pointing to `app/admin/dashboard.py`.

## Verification Plan

### Automated Tests
- **Unit Tests**: Test `IngestionService` with mocked `JobRepository`.
- **Integration Tests**: `pytest tests/integration/test_jobs.py`
    - Create a job via `ingest`.
    - Retrieve it via `GET /jobs`.
    - Check status updates.

### Manual Verification
1.  **Run Services**: `docker-compose up --build`
2.  **Access Dashboard**: Open `http://localhost:8501`.
3.  **Trigger Ingestion**: Send POST request to `/ingest/web`.
4.  **Verify Dashboard**:
    - Check if new job appears in the list.
    - Check status transition (RUNNING -> COMPLETED).
    - Introduce artificial failure (if possible) and test 'Retry'.
