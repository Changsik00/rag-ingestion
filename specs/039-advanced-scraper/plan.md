# Implementation Plan: Spec-039 (Refined)

## 📋 Branch Strategy
- `feature/039-advanced-scraper-refinement`

## 🛑 User Review Required
- **Firecrawl API Key**: Firecrawl 사용을 위해 API 키 설정 필요 (환경 변수 `FIRECRAWL_API_KEY`).
- **Trigger Thresholds**: 본문 최소 길이(300자) 등의 임계값 적절성 검토.

## 🎯 Core Strategy
- **Tiered Hybrid Scraper**: Trafilatura(Fast) -> Firecrawl(Semantic Advanced) -> Playwright(Custom Engine) 순의 계층적 구조.
- **Pre-processor (Pollution Control)**: 마크다운 생성 직후 실행되는 정밀 정규식 정제 엔진 구축.
- **Heuristic Quality Checker**: 스크래핑 결과의 '부실함'을 판단하는 전담 검증 클래스 도입.
- **Comparator Tool**: `scripts/compare_scrapers.py`를 통해 성능 지표(길이, 시간, 메타데이터) 시각화.

## 📂 Proposed Changes

### [Infrastructure Layer]

#### [NEW] `app/infrastructure/scraper/checker.py`
- 수집 결과의 품질(길이, 키워드, 구조)을 검사하여 Fallback 여부를 결정하는 `ScrapingQualityChecker`.

#### [NEW] `app/infrastructure/scraper/cleaner.py`
- 위키 문법, 특수 기호, 빈 표 등을 제거하는 `MarkdownCleaner`.

#### [NEW] `app/infrastructure/scraper/firecrawl_scraper.py`
- Firecrawl API를 활용한 시맨틱 마크다운 추출기.

#### [NEW] `app/infrastructure/scraper/playwright_scraper.py` (Extended)
- Playwright 기반의 커스텀 엔진 뼈대 유지.

#### [MODIFY] `app/infrastructure/scraper/composite_scraper.py`
- `ScrapingQualityChecker`와 연동하여 실시간 Fallback을 수행하는 통합 컨트롤러.

### [Utility]

#### [NEW] `scripts/compare_scrapers.py`
- Side-by-side 비교 및 성능 통계 리포트 생성 스크립트.

## 🧪 Verification Plan

### Automated Tests
- `tests/unit/infrastructure/scraper/test_cleaner.py`: 위키 노이즈 제거 패턴 검토.
- `tests/unit/infrastructure/scraper/test_checker.py`: Fallback 트리거 로직 검토.

### Manual Verification
1. **Wiki Cleanup**: 나무위키 URL 수집 후 `[1]`, `[편집]` 등이 사라졌는지 확인.
2. **Fallback Flow**: 텍스트가 짧은 페이지에서 자동으로 Firecrawl 호출 여부 로그 확인.
3. **Side-by-Side**: `compare_scrapers.py` 실행 결과물(Markdown 파일들) 대조.
