# Walkthrough: Spec-027 (Intelligent Web Scraping)

## 📌 Feature Summary
비용이 발생하는 외부 API 대신 오픈소스 **`trafilatura`**를 도입하여, 웹 페이지의 **본문(Article)**만 정밀하게 추출하는 `SmartWebScraper`를 구현했습니다.

## 🛠 Changes
### 1. `TrafilaturaWebScraper` 구현
- `BasicWebScraper` (requests+markdownify) -> `TrafilaturaWebScraper` 교체
- 광고, 댓글, 네비게이션 자동 제거
- 메타데이터(Title, Date, Author) 추출 기능 추가

### 2. Dependency Injection
- `dependencies.py`에서 `get_scraper()`가 `TrafilaturaWebScraper`를 반환하도록 변경

## 🧪 Verification
### Simulated Test (Ad Removal)
Mock HTML을 사용하여 광고 및 노이즈 제거 성능을 검증했습니다.

```python
# MOCK HTML Input
<html>
    <body>
        <nav>Menu 1 | Menu 2</nav>
        <div class="ad-container">Buy this product!</div>  <-- Removed
        <article>
            <h1>Real Content Title</h1>                    <-- Preserved
            <p>This is the main content.</p>
        </article>
        <div id="footer">Copyright 2026</div>              <-- Removed
    </body>
</html>
```

### Test Result
`tests/unit/infrastructure/scrapers/test_trafilatura_scraper.py` 통과.

```bash
tests/unit/infrastructure/scrapers/test_trafilatura_scraper.py ... [100%]
3 passed in 2.40s
```

## 📝 Conclusion
- **품질 향상**: 불필요한 노이즈가 제거되어 RAG 검색 품질이 향상될 것으로 기대됨.
- **비용 절감**: 외부 API 비용 없이 로컬 처리(CPU 기반)로 해결.
