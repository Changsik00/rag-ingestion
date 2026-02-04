# Implementation Plan - Spec 059: Docker Build Optimization

## 개요
Docker 빌드 속도 개선을 위해 공통 의존성을 포함한 Base Image를 구축하고, 각 서비스(`backend`, `rest`)가 이를 참조하도록 재구성합니다.

## Proposed Changes

### [Docker Infrastructure]

#### [NEW] [Dockerfile.base](file:///Users/ck/Project/doit/rag-ingestion/Dockerfile.base)
- Base: `python:3.12-slim`
- Install: `uv`, `ffmpeg`, `libmagic1`
- Copy: `pyproject.toml`, `uv.lock`
- Run: `uv sync --frozen --no-dev` & `playwright install chromium`

#### [MODIFY] [Dockerfile.backend](file:///Users/ck/Project/doit/rag-ingestion/Dockerfile.backend)
- `FROM rag-ingestion-base:latest`로 변경.
- 중복되는 의존성 설치 단계(`apt-get`, `uv sync` 등) 제거 또는 최소화.
- 소스 코드(`app/`) 복사 및 실행 명령어 유지.

#### [MODIFY] [Dockerfile.admin](file:///Users/ck/Project/doit/rag-ingestion/Dockerfile.admin)
- `FROM rag-ingestion-base:latest`로 변경.
- 중복되는 의존성 설치 단계 제거.
- 소스 코드(`admin/`) 복사 및 실행 명령어 유지.

#### [MODIFY] [docker-compose.yml](file:///Users/ck/Project/doit/rag-ingestion/docker-compose.yml)
- (옵션) `base` 서비스 추가 또는 주석으로 빌드 가이드 명시.
- `backend` 및 `admin` 서비스가 로컬 이미지를 바라보도록 `pull_policy: never` (또는 `build` 컨텍스트 유지하되 캐시 활용).

#### [NEW] [Makefile](file:///Users/ck/Project/doit/rag-ingestion/Makefile)
- `build-base`: `docker build -t rag-ingestion-base:latest -f Dockerfile.base .` 명령어 편의성 제공.
- `up`: `make build-base && docker compose up -d --build`

---

## Verification Plan

### Manual Verification
1.  **Baseline Check**: 현재 상태에서 `docker compose build` 시간을 측정합니다.
    ```bash
    time docker compose build
    ```
2.  **Base Image Build**:
    ```bash
    docker build -t rag-ingestion-base:latest -f Dockerfile.base .
    ```
3.  **Service Rebuild (Code Change)**:
    - `app/interfaces/api/main.py` 등 소스 코드에 주석 하나를 추가/변경.
    - `docker compose build backend` 실행 시간 비교.
    - **Expected**: 수 초 이내 완료 (기존에는 수 분 소요되었을 것).
4.  **Functionality Check**:
    - 컨테이너 구동 후 `curl localhost:8000/health` 정상 응답 확인.
    - Admin 페이지 접속 확인.
