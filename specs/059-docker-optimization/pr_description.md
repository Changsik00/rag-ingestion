# feat(spec-059): docker build optimization

## 📋 Summary

### 배경 및 목적
기존 Docker 빌드 시마다 `torch`, `playwright`, `ffmpeg` 등 무거운 의존성을 반복적으로 설치하여 개발 루프가 느려지는 문제가 있었습니다. 이를 해결하기 위해 공통 의존성을 포함한 **Base Image**를 도입하여 빌드 시간을 획기적으로 단축했습니다.

### 주요 변경 사항
- [x] **Base Image 도입**: `Dockerfile.base`를 신설하여 시스템 패키지 및 Python Heavy Dependencies(`uv sync`, `playwright install`)를 미리 빌드.
- [x] **Service Optimization**: `backend` 및 `admin` Dockerfile이 `rag-ingestion-base`를 참조하도록 변경하여, 소스 코드 변경 시 재빌드 시간을 **수 초(Seconds)** 단위로 단축.
- [x] **Makefile 추가**: `make build-base`, `make up` 등 개발 편의성을 위한 명령어 세트 제공.

## 🎯 Key Review Points
1. **Dependent Services**: Backend와 Admin 컨테이너가 정상적으로 Base Image를 참조하고 구동되는지.
2. **Build Process**: `make up` 명령어를 통해 로컬 환경에서 원활하게 빌드 및 실행이 되는지.

## 🧪 Verification

### Build Speed Test
- **Before**: 전체 리빌드 시 약 3~5분 소요 (의존성 체크 및 설치)
- **After**: `make up` 실행 시 (Base Image 존재 시) **약 5초 내외**로 서비스 구동 완료.

### Functionality Test
```bash
make up
curl localhost:8000/docs  # 200 OK
curl localhost:8501       # 200 OK
```

## 📦 Files Changed

### 🆕 New Files
- `Dockerfile.base`: 공통 기반 이미지 정의
- `Makefile`: 빌드 및 실행 편의 스크립트
- `specs/059-docker-optimization/`: 관련 문서 일체

### 🛠 Modified Files
- `Dockerfile.backend`: Base Image 적용, 의존성 설치 로직 제거
- `Dockerfile.admin`: Base Image 적용, 의존성 설치 로직 제거
- `README.md`: 빌드 및 배포 가이드 업데이트

## ✅ Definition of Done
- [x] Base Image 빌드 및 로컬 태깅 확인
- [x] 모든 서비스 정상 구동 확인
- [x] `walkthrough.md`, `pr_description.md` 작성 완료
- [x] `README.md` 업데이트 완료
