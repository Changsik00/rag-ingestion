# feat(spec-047): implement YouTube knowledge scraper with Intel Mac optimization

## 📋 Summary

### 배경 및 목적
- 기존 텍스트 중심 스크래핑에서 YouTube 영상 콘텐츠로 지식 수집 범위를 확장함.
- 영상의 단순 자막 수집을 넘어, LLM을 활용해 핵심 주장, 주제별 요약 등을 포함한 "영상 지적 문서" 생성이 목표임.
- 사용자의 Intel Core i9 Mac 환경에서 로컬 STT(Whisper)가 원활히 작동하도록 하드웨어 최적화를 수행함.

### 주요 변경 사항
- [x] **YouTubeScraper 구현**: `youtube-transcript-api` 및 `yt-dlp` 통합.
- [x] **Whisper Fallback**: 자막 부재 시 로컬 Whisper 모델(`compute_type="int8"`)을 사용한 STT 기능 추가.
- [x] **LLM 지식 추출**: 영상 스크립트에서 요약, 주장, 의도 등을 추출하는 구조화 로직 구현.
- [x] **CompositeScraper 통합**: YouTube URL 자동 감지 및 라우팅 로직 추가.
- [x] **운영 가이드 작성**: Intel Mac 최적화 및 배포 전략 가이드(`docs/design_guides/011-youtube-strategy.md`) 작성.

## 🎯 Key Review Points
1. **Intel i9 최적화**: `faster-whisper` 설정에서 `device="cpu"` 및 `compute_type="int8"`이 적절히 적용되었는지 확인 부탁드립니다.
2. **Fallback 로직**: 자막 수집 실패 시 자동으로 오디오 추출 및 STT로 이어지는 흐름의 안정성.
3. **LLM 프롬프트**: 영상 스크립트에서 구조화된 JSON을 추출하기 위한 프롬프트의 명확성.

## 🧪 Verification

### Automated Tests
```bash
uv run pytest tests/unit/infrastructure/scrapers/test_youtube_scraper.py
```
**테스트 결과 요약:**
- ✅ `test_youtube_scraper_with_transcript`: 자막 존재 시 정상 추출 완료.
- ✅ `test_youtube_scraper_fallback_to_whisper`: 자막 부재 시 Whisper STT Fallback 정상 작동.

### Manual Verification (Scenarios)
1. **YouTube URL 처리**: `CompositeScraper`가 `youtube.com/watch?v=...` URL을 감지하여 `YouTubeScraper`로 작업을 위임함.
2. **오디오 추출 및 삭제**: `yt-dlp`로 임시 MP3 파일을 생성한 후, STT 완료 시 즉시 삭제하여 메모리/디스크 오염 방지.

## 📦 Files Changed

### 🆕 New Files
- `app/infrastructure/scrapers/youtube_scraper.py`: YouTube 전용 스크래퍼 로직
- `tests/unit/infrastructure/scrapers/test_youtube_scraper.py`: 단위 테스트
- `docs/design_guides/011-youtube-strategy.md`: 하드웨어 최적화 가이드
- `specs/047-youtube-knowledge-scraper/*`: 설계 및 작업 증적 (Spec, Plan, Task, Walkthrough)

### 🛠 Modified Files
- `app/infrastructure/scrapers/composite_scraper.py`: YouTube 라우팅 로직 추가
- `app/use_cases/ingestion.py`: LLM 인터페이스 주입 로직 추가
- `backlog/queue.md`: 작업 상태 업데이트

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
