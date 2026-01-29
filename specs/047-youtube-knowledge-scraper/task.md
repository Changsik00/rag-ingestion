# Task List: Spec 047 - YouTube Knowledge Scraper

## Progress
- [x] Spec 번호 확정 및 브랜치 생성 (`feature/047-youtube-knowledge-scraper`)
- [x] spec.md 작성 (Korean Context)
- [x] plan.md 작성 (Korean Strategy)
- [x] task.md 작성 (현 파일)
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Environment & Dependency Setup
- [x] 의존성 라이브러리 추가: `uv add youtube-transcript-api yt-dlp faster-whisper`
- [x] 로컬 환경 `ffmpeg` 설치 확인 및 안내 가이드 작성
- [x] Commit: `chore(spec-047): add youtube scraping and stt dependencies`

## Task 2: Infrastructure Layer - YouTube Scraper
### 2-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/infrastructure/scrapers/test_youtube_scraper.py`
- [x] Test 실행 (Fail -> Pass)
- [x] Commit: `test(spec-047): add youtube scraper unit tests`

### 2-2. Implementation: Transcript & Audio
- [x] `YouTubeScraper` 골격 구현 및 `youtube-transcript-api` 연동
- [x] `yt-dlp`를 활용한 오디오 추출 및 처리 로직 구현
- [x] `faster-whisper` 연동 및 Fallback 로직 구현
- [x] Commit: `feat(spec-047): implement transcript retrieval and whisper fallback`

### 2-3. Implementation: LLM Knowledge Extraction
- [x] LLM 프롬프트 설계 (주제 분할, 주장 추출, 의도 분석)
- [x] 지능형 스크립트 정제 로직 구현
- [x] Commit: `feat(spec-047): add llm-based video knowledge extraction`

## Task 3: Integration & Documentation
- [x] `CompositeScraper`에 YouTube 라우팅 로직 추가
- [x] **운영 전략 가이드 작성**: `docs/design_guides/011-youtube-strategy.md` (Intel Mac 최적화 포함)
- [x] Commit: `docs(spec-047): add youtube scraping strategy and mac optimization guide`

---

## Task N: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/047-youtube-knowledge-scraper/walkthrough.md`
- [x] **PR Description 작성**: `specs/047-youtube-knowledge-scraper/pr_description.md`
- [x] **Archive Commit**: 위 파일을 `specs/`에 커밋
- [x] Create PR: `gh pr create`

## Summary
**총 Task**: 3개 주요 작업군  
**예상 커밋 수**: 7~9개  
**현재 진행**: 완료 (PR #51 생성됨)
