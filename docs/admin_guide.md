# Admin Dashboard User Guide

이 문서는 Ingestion 작업을 모니터링하고 관리할 수 있는 Streamlit 기반 Admin Dashboard 사용법을 설명합니다.

## 1. 개요
Admin Dashboard는 다음 기능을 제공합니다:
- **작업 상태 모니터링**: Ingestion 작업의 진행 상황(PENDING, RUNNING, COMPLETED, FAILED)과 결과를 실시간으로 확인합니다.
- **작업 상세 조회**: 특정 작업의 소스 URL, 생성/업데이트 시간, 에러 메시지 등 상세 정보를 조회합니다.
- **실패 작업 재시도**: 실패한(FAILED) 작업에 대해 즉시 재시도(Retry)를 요청할 수 있습니다.

## 2. 실행 방법

Docker Compose를 사용하여 전체 스택(Backend, Neo4j, ChromaDB, Streamlit)을 한 번에 실행합니다.

```bash
docker compose up --build
```

실행 후 브라우저에서 아래 주소로 접속합니다:
- **Admin Dashboard**: [http://localhost:8501](http://localhost:8501)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

> **참고**: `docker-compose.yml`에는 `backend`와 `streamlit` 서비스가 모두 포함되어 있어, 별도의 로컬 서버 실행이 필요 없습니다. `streamlit` 컨테이너는 내부 네트워크를 통해 `backend`와 통신합니다.

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
