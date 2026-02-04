# Spec 059: Docker Build Optimization

## 1. 개요 (Overview)
현재 RAG Ingestion 프로젝트의 Docker 빌드 시간이 `torch`, `playwright`, `langchain` 등 무거운 의존성 설치로 인해 과도하게 소요되고 있습니다. 특히 `backend`와 `admin` 서비스가 동일한 의존성을 중복으로 설치하는 비효율이 존재합니다. 본 스펙은 공통 의존성을 포함한 **Base Image**를 도입하여 빌드 시간을 단축하고 캐싱 효율을 극대화하는 것을 목표로 합니다.

## 2. 목표 (Goals)
*   **빌드 시간 단축**: 무거운 라이브러리(PyTorch, Transformers, Playwright Browsers) 설치 과정을 Base Image로 분리하여 재빌드 시 소요 시간을 최소화합니다.
*   **중복 제거**: `backend`와 `admin` 컨테이너가 동일한 Base Image를 공유하도록 하여 스토리지 및 네트워크 대역폭 낭비를 줄입니다.
*   **개발 생산성 향상**: 코드 변경 시 즉각적인 빌드 피드백을 받을 수 있는 환경을 조성합니다.

## 3. 상세 설계 (Technical Design)

### 3.1 Base Image 전략
*   **Dockerfile.base** 신설:
    *   OS: `python:3.12-slim`
    *   System Depts: `ffmpeg`, `libmagic1`, `curl`, `git` 등 공통 패키지.
    *   Python Depts: `pyproject.toml` 및 `uv.lock` 기반의 `uv sync` 실행 (Heavy Libraries 포함).
    *   Playwright: `playwright install chromium` 실행.
*   **Tagging**: 로컬 개발 환경에서는 `rag-ingestion-base:latest` 태그를 사용합니다.

### 3.2 Service Dockerfiles 수정
*   **Backend (`Dockerfile.backend`)**:
    *   `FROM rag-ingestion-base:latest`
    *   `app/` 소스 코드 복사.
    *   `uv sync` (코드 변경에 따른 가벼운 동기화만 수행).
*   **Admin (`Dockerfile.admin`)**:
    *   `FROM rag-ingestion-base:latest`
    *   `admin/` 소스 코드 복사.

### 3.3 Docker Compose 구성
*   `services` 섹션에 `base` 서비스를 추가하는 대신, 별도의 빌드 스크립트(`Makefile` 또는 `deploy.sh`)를 통해 Base Image를 먼저 빌드하도록 가이드하거나, `docker build` 명령어를 명시합니다. (Docker Compose file format 3.x에서는 `depends_on`으로 빌드 순서 제어가 완벽하지 않을 수 있으므로, 명시적 가이드가 안전함)
*   *Alternative*: `docker-compose.yml` 내 `base` 서비스를 정의하고 `image: rag-ingestion-base:latest`를 지정, 다른 서비스들이 이를 참조하도록 설정.

## 4. 기대 효과 (Expected Impact)
*   **Initialization Time**: 최초 빌드 시간은 동일하나, 이후 소스 코드 변경 시 빌드 시간이 수 분 -> 수 초로 단축됨.
*   **Resource Usage**: 디스크 공간 절약 (Layer Sharing).

## 5. 제외 범위 (Non-Goals)
*   CI/CD 파이프라인 상의 Remote Registry Push (로컬 최적화 우선).
*   Production용 Multi-stage Build의 극단적 경량화 (개발/테스트 속도 우선).
