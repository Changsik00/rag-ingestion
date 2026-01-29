# PR Description: Spec 048 - Docker Environment Sync for YouTube & Web Scraping

## Summary
YouTube 수집(Whisper STT) 및 Playwright 기반 웹 스크래핑 기능이 Docker 환경에서 정상 작동하도록 `Dockerfile.backend`를 업데이트했습니다.

## Key Changes
- **FFmpeg 설치**: Whisper STT 오디오 처리를 위해 `ffmpeg` 설치 구문 추가.
- **Playwright 브라우저 & 의존성**: Chromium 브라우저와 실행에 필요한 시스템 라이브러리(`libnss3`, `libatk` 등) 설치 로직 통합.

## Verification Plan
1. `Dockerfile.backend` 빌드 테스트 (Syntactic check).
2. 바이너리 존재 유무 확인 가이드 작성.

## Impact
- Docker 이미지 크기가 증가하지만, 런타임 안정성과 환경 정합성을 동시에 확보했습니다.
