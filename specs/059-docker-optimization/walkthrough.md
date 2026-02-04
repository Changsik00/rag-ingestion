# Walkthrough - Spec 059: Docker Build Optimization

## 1. Changes Overview

### 1-1. Base Image Introduction
*   **[NEW]** `Dockerfile.base`:
    *   `python:3.12-slim` 기반
    *   **Common Deps**: `ffmpeg`, `libmagic1`, `git`, `curl`
    *   **Heavy Libs**: `transformers`, `torch`, `playwright` (via `uv sync`)
    *   **Browsers**: `playwright install chromium`
*   **[NEW]** `Makefile`:
    *   `make build-base`: Base Image 빌드 및 로컬 태깅 (`rag-ingestion-base:latest`)
    *   `make up`: Base Image 빌드 후 서비스 실행

### 1-2. Service Dockerfiles Optimization
*   **[MODIFY]** `Dockerfile.backend` & `Dockerfile.admin`:
    *   `FROM rag-ingestion-base:latest`로 변경.
    *   개별 의존성 설치(`apt-get`, `uv sync`, `playwright install`) 단계 제거.
    *   소스 코드(`app/`, `admin/`)만 복사(COPY)하여 빌드 속도 극대화.

## 2. Verification Results

### 2-1. Build Time Comparison
*   **Before**: 서비스 재빌드 시 의존성 확인 및 시스템 패키지 체크로 약 1~3분 소요.
*   **After**: 소스 코드 변경 후 `make up` 실행 시 **수 초(Seconds)** 내 완료. (Layer Caching 극대화)

### 2-2. Functionality Verification
*   **Backend**: `curl localhost:8000/docs` -> 200 OK ✅
*   **Admin**: `curl localhost:8501` -> 200 OK ✅
*   **Integration**: `make up` 명령어로 전체 스택 정상 구동 확인.

## 3. Usage Guide
```bash
# 최초 실행 시 (Base Image 빌드 포함)
make up

# 서비스만 재시작
docker compose up -d
```
