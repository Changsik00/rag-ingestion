# Implemention Plan - Spec 003: Ingestion Admin Dashboard (Streamlit)

## Goal
수집(Ingestion) 작업의 상태를 모니터링하고, 실패한 작업을 재시도할 수 있는 Streamlit 기반의 Admin Dashboard를 구현합니다.

## Proposed Changes

### Domain Layer
#### [NEW] [app/domain/entities/job.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/entities/job.py)
- `IngestionJob` 엔티티 정의
- `JobStatus` Enum 정의 (PENDING, RUNNING, COMPLETED, FAILED)

#### [NEW] [app/domain/interfaces/job_repository.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/interfaces/job_repository.py)
- `JobRepository` 인터페이스 정의

### Infrastructure Layer
#### [NEW] [app/infrastructure/storage/neo4j_job_repo.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/neo4j_job_repo.py)
- `Neo4jJobRepository` 구현
- 메서드: `create_job`, `update_job`, `get_job`, `list_jobs`

### Application Layer
#### [MODIFY] [app/application/use_cases/ingestion.py](file:///Users/ck/Project/doit/rag-ingestion/app/application/use_cases/ingestion.py)
- `IngestionService`가 `JobRepository`를 의존하도록 수정
- 작업 시작/종료/실패 시 Job 상태 업데이트 로직 포장(Wrap)

### Interface Layer (API)
#### [NEW] [app/interface/api/endpoints/jobs.py](file:///Users/ck/Project/doit/rag-ingestion/app/interface/api/endpoints/jobs.py)
- `GET /jobs`: 작업 목록 조회
- `GET /jobs/{job_id}`: 작업 상세 조회
- `POST /jobs/{job_id}/retry`: 작업 재시도

#### [MODIFY] [app/main.py](file:///Users/ck/Project/doit/rag-ingestion/app/main.py)
- `jobs_router` 등록
- `JobRepository` 의존성 주입 설정

### Admin Dashboard (Streamlit)
#### [NEW] [app/admin/dashboard.py](file:///Users/ck/Project/doit/rag-ingestion/app/admin/dashboard.py)
- Streamlit 애플리케이션 진입점
- FastAPI 엔드포인트와 통신하여 데이터 시각화

#### [NEW] [app/admin/pages/](file:///Users/ck/Project/doit/rag-ingestion/app/admin/pages/)
- (옵션) 기능이 복잡해질 경우 페이지 분리

### Configuration
#### [MODIFY] [docker-compose.yml](file:///Users/ck/Project/doit/rag-ingestion/docker-compose.yml)
- `streamlit` 서비스 추가 (포트 8501)

## Verification Plan

### Automated Tests
- **Unit Tests**: `IngestionService`와 Mock `JobRepository` 테스트
- **Integration Tests**: `pytest tests/integration/test_jobs.py`
    - 작업을 생성하고 `GET /jobs`로 조회 확인
    - 상태 변경 확인
    - 재시도 로직 동작 확인

### Manual Verification
1.  **서비스 실행**: `docker-compose up --build`
2.  **대시보드 접속**: `http://localhost:8501` 접속
3.  **수집 요청**: `POST /ingest/web` 요청 전송
4.  **대시보드 확인**:
    - 리스트에 새로운 작업 표시 확인
    - 상태 변화 (RUNNING -> COMPLETED) 확인
    - (가능하다면) 실패 상황 연출 후 'Retry' 버튼 동작 확인
