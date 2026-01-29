# Walkthrough: Spec 047 - YouTube Knowledge Scraper

## 🚀 개요
YouTube 영상의 URL을 입력받아 **"영상 지식 문서"**라는 고품질 구조화 데이터를 생성하는 기능을 구현했습니다. 
특히 사용자의 **Intel Core i9 Mac** 환경에서 최적의 성능을 낼 수 있도록 `faster-whisper` 모델의 **Quantization(int8)** 설정을 적용했습니다.

## ✨ 주요 구현 사항

### 1. YouTube 전용 스크래퍼 (`YouTubeScraper`)
- **다중 소스 수집**: `youtube-transcript-api`를 통해 수동/자동 자막을 우선 수집합니다.
- **Whisper Fallback**: 자막이 없거나 품질이 낮은 경우, `yt-dlp`로 오디오를 추출하여 로컬 Whisper 모델로 STT를 수행합니다.
- **Intel i9 최적화**: `compute_type="int8"` 및 CPU 스레드 최적화를 통해 로컬에서도 빠른 STT 속도를 확보했습니다.

### 2. LLM 기반 지식 구조화
- 단순 텍스트 스크립트를 LLM에 전달하여 다음 정보를 추출합니다:
  - 핵심 요약 (Summary)
  - 주제별 타임라인 (Topics/Sections)
  - 주요 주장 및 사실 (Claims)
  - 영상의 어조와 제작 의도 (Tone & Intent)

### 3. 유연한 통합 (`CompositeScraper`)
- `CompositeScraper`가 YouTube URL을 자동 감지하여 처리하도록 라우팅 로직을 추가했습니다.
- `IngestionService`를 통해 중앙 집중식 LLM 주입이 가능하도록 설계했습니다.

## 🧪 테스트 결과

### 단위 테스트 (`pytest`)
- 자막이 있는 경우의 정상 동작 확인.
- 자막이 없는 경우 Whisper STT로 Fallback 되는 로직 확인.
- Pydantic v2 필드 호환성 검증 완료.

```bash
uv run pytest tests/unit/infrastructure/scrapers/test_youtube_scraper.py
# Result: 2 passed in 0.16s
```

## 📂 관련 문서
- [Spec 047 설계 문서](file:///Users/ck/Project/doit/rag-ingestion/specs/047-youtube-knowledge-scraper/spec.md)
- [Intel Mac 최적화 가이드](file:///Users/ck/Project/doit/rag-ingestion/docs/design_guides/011-youtube-strategy.md)
