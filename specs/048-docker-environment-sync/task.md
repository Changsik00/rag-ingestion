# Task List: Spec 048 - Docker Environment Sync

## Progress
- [x] Spec 번호 확정 (048)
- [x] Spec/Plan/Task 골격 생성
- [x] User Plan Accept

## Task 1: Dockerfile Update
- [x] `Dockerfile.backend` 수정: `ffmpeg` 추가
- [x] `Dockerfile.backend` 수정: Playwright 의존성 및 브라우저 설치 추가
- [x] Docker 캐시 최적화 (Layer 분리)

## Task 2: Verification
- [x] Docker 이미지 빌드 테스트
- [x] 컨테이너 내부 바이너리 작동 확인 (`ffmpeg`, `playwright`)
- [x] STT 로직 및 Playwright 수집 로직 Docker 내 실행 시뮬레이션

## Task 3: Finalize
- [x] Walkthrough 작성
- [x] PR 생성
