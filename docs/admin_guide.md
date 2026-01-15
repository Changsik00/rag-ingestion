# Admin Dashboard User Guide

이 문서는 Ingestion 작업을 모니터링하고 관리할 수 있는 Streamlit 기반 Admin Dashboard 사용법을 설명합니다.

## 1. 개요
Admin Dashboard는 다음 기능을 제공합니다:
- **작업 상태 모니터링**: Ingestion 작업의 진행 상황(PENDING, RUNNING, COMPLETED, FAILED)과 결과를 실시간으로 확인합니다.
- **작업 상세 조회**: 특정 작업의 소스 URL, 생성/업데이트 시간, 에러 메시지 등 상세 정보를 조회합니다.
- **실패 작업 재시도**: 실패한(FAILED) 작업에 대해 즉시 재시도(Retry)를 요청할 수 있습니다.

## 2. 실행 방법

Docker Compose를 사용하여 백엔드(Neo4j, ChromaDB, Streamlit) 서비스를 모두 실행합니다.

```bash
docker compose up --build
```

실행 후 브라우저에서 아래 주소로 접속합니다:
- **Admin Dashboard**: [http://localhost:8501](http://localhost:8501)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs) (백엔드 서버 로컬 실행 시)

> **참고**: 현재 구성에서 백엔드 API(FastAPI)는 호스트 머신에서 별도로 실행하거나, Docker Compose 외부에서 실행해야 할 수 있습니다(개발 환경). Streamlit 컨테이너는 주소 `http://host.docker.internal:8000`을 통해 로컬 백엔드에 접속하도록 설정되어 있습니다.

## 3. 주요 기능

### 3.1 대시보드 메인
- **KPI 지표**: 전체 작업 수, 실패한 작업 수, 진행 중인 작업 수를 상단에서 한눈에 볼 수 있습니다.
- **Job List**: 최근 작업 목록을 테이블 형태로 표시하며, 상태에 따라 색상(초록, 빨강, 회색)이 구분됩니다.

### 3.2 작업 상세 및 재시도
1.  **Select Job**: 목록에서 확인하고 싶은 작업 ID를 선택합니다.
2.  **Job Details**: 선택한 작업의 상세 정보(JSON)가 확장 패널에 표시됩니다.
3.  **Retry**: 작업 상태가 `FAILED`인 경우, `Retry Job {ID}` 버튼이 활성화됩니다. 클릭 시 해당 URL에 대해 새로운 Ingestion 작업을 트리거합니다.

## 4. 트러블슈팅

### 백엔드 연결 실패
화면에 "Failed to connect to Backend" 메시지가 표시되는 경우:
1.  백엔드 API 서버(`uv run fastapi dev app/interfaces/api/main.py`)가 실행 중인지 확인하세요.
2.  `docker-compose.yml`의 `API_URL` 환경변수가 올바른지 확인하세요 (기본값: `http://host.docker.internal:8000`).

### 재시도 실패
- 재시도 요청이 실패하는 경우, 작업 ID가 유효한지 또는 백엔드 로그에 에러가 없는지 확인하세요.
