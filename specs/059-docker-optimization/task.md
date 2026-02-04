# Task List: Spec-059 (Docker Build Optimization)

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] User Plan Accept

---

## Task 1: Base Image Construction
- [x] `Dockerfile.base` 작성: 공통 시스템 패키지 및 Python 의존성 설치
- [x] Base Image 빌드 및 로컬 태깅 (`rag-ingestion-base:latest`)
- [/] `docker-compose.yml`에 Base Image 빌드 서비스 추가 (선택적)

## Task 2: Service Dockerfiles Update
- [x] `Dockerfile.backend`: Base Image 활용하도록 수정 (의존성 설치 단계 제거)
- [x] `Dockerfile.admin`: Base Image 활용하도록 수정 (의존성 설치 단계 제거)

## Task 3: Verification
- [x] Docker Compose 전체 리빌드 테스트 (`docker compose up --build`)
- [x] 각 서비스 정상 구동 확인 (Backend, Admin)
- [x] 빌드 시간 단축 효과 확인

## Task 4: Documentation & Cleanup
- [x] `README.md` 내 Docker 빌드 가이드 업데이트 (Base Image 관련 내용)
- [x] `walkthrough.md` 작성
- [x] PR 생성
