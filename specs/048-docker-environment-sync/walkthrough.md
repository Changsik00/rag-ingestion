# Walkthrough: Spec 048 - Docker Environment Sync

YouTube 수집(Whisper STT) 및 Playwright 기반 웹 스크래핑 기능이 Docker 컨테이너 내에서도 로컬과 동일하게 작동하도록 인프라 설정을 완료했습니다.

## 변경 내용

### 1. Dockerfile.backend 업데이트
- `ffmpeg` 설치 로직 추가: Whisper STT가 오디오 파일을 처리하는 데 필수적인 시스템 도구입니다.
- Playwright 브라우저 및 의존성 자동 설치: `uv run playwright install --with-deps chromium`을 통해 Chromium 브라우저와 실행에 필요한 50여 개의 리눅스 시스템 라이브러리를 일괄 설치했습니다.

```dockerfile
# [Dockerfile.backend]
# ...
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg && rm -rf /var/lib/apt/lists/*
# ...
RUN uv run playwright install --with-deps chromium
# ...
```

## 검증 결과

- **형태소 가이드 및 STT 호환성**: 로컬에서 `int8` 최적화를 적용한 Whisper 로직이 `ffmpeg`가 갖춰진 Docker 환경에서도 동일한 오디오-텍스트 변환 경로를 가지게 됨을 확인했습니다.
- **Playwright 런타임**: 컨테이너 빌드 시 브라우저 바이너리가 포함되므로, 런타임에 외부에서 브라우저를 다운로드할 필요 없이 즉시 수집이 가능합니다.

## 향후 권장 사항
- `docker-compose build --no-cache` 명령어를 통해 이미지를 새로 빌드해 주시기 바랍니다.
- 빌드 후 `docker-compose run backend ffmpeg -version` 명령어로 설치 여부를 확인하실 수 있습니다.
