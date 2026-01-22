# Spec-027: Intelligent Web Scraping (Content Cleaning)

## 📋 배경 및 문제 정의 (Background & Problem)
현재의 `BasicWebScraper` (`requests` + `markdownify`) 방식은 HTML 전체를 단순 변환하므로 광고, 네비게이션, 댓글 등 노이즈 데이터가 RAG 파이프라인에 유입됩니다(정보 오염).
이를 해결하기 위해 비용이 들지 않는 오픈소스 라이브러리인 **`trafilatura`**를 도입하여, 본문(Article)만 정밀하게 추출하고 오염을 방지해야 합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **Trafilatura Integration**:
    - `BasicWebScraper`를 대체하거나 새로운 `SmartWebScraper` 구현체를 만듭니다.
    - `trafilatura` 라이브러리를 사용하여 URL fetch 및 Main Content Extract를 수행합니다.
2.  **Metadata Extraction**:
    - `Trafilatura`의 기능을 활용하여 Title, Author, Date, Site Name, Description 등의 메타데이터를 구조적으로 추출해야 합니다.
3.  **Fallback Strategy**:
    - `Trafilatura`가 실패(None 반환)할 경우, 기존 `BasicWebScraper` 로직(또는 단순 HTML 텍스트 추출)으로 Fallback 하여 수집 실패를 방지해야 합니다.

### Non-Functional Requirements
1.  **Zero Cost**: 외부 유료 API(Firecrawl 등)를 사용하지 않고 Local Processing으로 처리해야 합니다.
2.  **Clean Output**: 결과물 Markdown에는 광고 스크립트, 메뉴, 푸터 등이 제거되어야 합니다.

## ✅ Definition of Done
1.  **Dependency Added**: `pyproject.toml`에 `trafilatura` 추가.
2.  **Unit Tests Pass**: `tests/unit/infrastructure/scrapers/test_trafilatura_scraper.py` 통과 (광고 제거 검증).
3.  **Real-world Verification**: 실제 뉴스/블로그 URL 테스트 시 깨끗한 본문만 추출되는지 `walkthrough.md`에 증거 포함.
