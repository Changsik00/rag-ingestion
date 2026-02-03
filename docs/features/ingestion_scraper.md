# 📝 RAG 데이터 인제스션: 스크래핑 전략 가이드

이 문서는 웹 원문 데이터를 임베딩하기 전, 최적의 마크다운 형태로 추출하기 위한 스크래퍼 운영 및 고도화 전략을 다룹니다.

---

## 1. TrafilaturaWebScraper 보완 전략

`Trafilatura`는 빠르고 가볍지만, 정적 HTML 분석에 의존합니다. 현재 코드를 더 견고하게 만들기 위해 다음 사항을 보완해야 합니다.

### 주요 보완 사항

* **User-Agent 설정:** 봇 차단을 방지하기 위해 실제 브라우저처럼 보이는 헤더를 추가해야 합니다.
* **에러 핸들링 강화:** 단순 `Exception` 외에 HTTP 상태 코드별(403, 404, 429) 대응 로직이 필요합니다.
* **정규식(Regex) 정밀화:** 특정 패턴의 빈 표뿐만 아니라, 불필요한 특수문자 파편을 제거하는 로직을 범용적으로 개선합니다.

### 보완된 코드 예시

```python
def _clean_markdown(self, text: str) -> str:
    # 1. 다중 공백 및 빈 줄 정제
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # 2. 나무위키/위키피디아식 각주 [1], [편집] 제거
    text = re.sub(r'\[\d+\]|\[편집\]', '', text)
    # 3. 비어있는 마크다운 링크 제거 [ ]()
    text = re.sub(r'\[\s*\]\(\s*\)', '', text)
    return text.strip()

# fetch_url 호출 시 User-Agent 추가
downloaded = trafilatura.fetch_url(url, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...")

```

---

## 2. FirecrawlWebScraper 도입 가이드

나무위키와 같이 자바스크립트 실행이 필수적인 사이트를 위해 **Firecrawl**을 도입합니다.

### 특징

* **Headless Browser 내장:** 내부적으로 Playwright를 사용하여 JS를 실행합니다.
* **LLM-Ready:** 단순 추출이 아닌, AI 모델이 이해하기 가장 좋은 형태로 HTML을 재구성하여 마크다운을 생성합니다.

### 구현 가이드 (Python)

1. **설치:** `pip install firecrawl-py`
2. **구현:**

```python
from firecrawl import FirecrawlApp

class FirecrawlWebScraper(ScraperInterface):
    def __init__(self, api_key: str):
        self.app = FirecrawlApp(api_key=api_key)

    def scrape(self, url: str) -> IngestResponse:
        # formats=['markdown'] 설정으로 최적화된 결과 수신
        result = self.app.scrape_url(url, params={
            'formats': ['markdown'],
            'onlyMainContent': True,
            'waitFor': 2000  # 동적 요소 로드를 위한 대기 시간
        })
        return IngestResponse(
            url=url,
            markdown=result['markdown'],
            metadata=result.get('metadata', {})
        )

```

---

## 3. 스크래퍼 비교: Trafilatura vs. Firecrawl

| 비교 항목 | Trafilatura | Firecrawl |
| --- | --- | --- |
| **작동 방식** | 정적 HTML 파싱 (Fast) | Headless 브라우저 렌더링 (Deep) |
| **JS 렌더링** | **지원 안 함** | **완벽 지원** |
| **나무위키 대응** | 본문 누락 가능성 높음 | 매우 깔끔하게 추출 가능 |
| **인프라 비용** | 무료, 로컬 라이브러리 | API 비용 발생 또는 셀프 호스팅 |
| **권장 용도** | 뉴스, 블로그, 정적 위키 | SPA, 복잡한 테이블, 동적 웹사이트 |

---

## 4. 결과물 품질 비교 방법 (Evaluation Metrics)

스크래퍼의 성능을 평가할 때는 다음 3가지 지표를 기준으로 원문을 대조합니다.

### 체크리스트

1. **내용 완결성 (Recall):** 원문의 핵심 내용(텍스트)이 누락되지 않고 모두 포함되었는가?
2. **구조 보존성 (Structure):** 표(Table)의 행/열 관계가 깨지지 않았는가? `#` 헤더가 논리적 위계에 맞게 뽑혔는가?
3. **노이즈 밀도 (Noise Rate):** 본문과 상관없는 광고, 내비게이션 메뉴, 각주 숫자가 얼마나 섞여 있는가?

### 실무 비교 팁

* **Visual Diff 도구 활용:** 두 스크래퍼의 결과물(`output.md`)을 VS Code의 `Compare Selected` 기능으로 열어 어느 쪽이 실제 문맥을 더 잘 유지하는지 눈으로 확인합니다.
* **토큰 효율성 측정:** 동일한 정보를 전달하면서 불필요한 특수문자가 적은 쪽이 임베딩 비용과 검색 정확도 면에서 유리합니다.

---

> **Note:** 우선 순위가 높은 타겟(나무위키 등)에 대해서는 **Firecrawl**을 먼저 적용해 보고, 데이터 양이 방대해질 경우 상대적으로 단순한 사이트들을 **Trafilatura**로 처리하는 하이브리드 전략을 추천합니다.
