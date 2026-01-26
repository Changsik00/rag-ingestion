# Spec-039: Advanced Scraper (Pollution Control & Hybrid Strategy)

## 📋 배경 및 문제 정의 (Background & Problem)
단순한 텍스트 추출을 넘어, RAG 인덱싱의 품질을 결정짓는 '데이터 청결도'와 '구조적 완성도'를 확보해야 함.
1. **데이터 오염**: 위키 각주, 편집 버튼, 네비게이션 박스 등 RAG 성능을 저하시키는 '시맨틱 노이즈'가 다수 포함됨.
2. **부실한 결과 처리**: 자바스크립트 차단으로 인한 빈 페이지나 구조가 깨진 마크다운이 수집되어도 이를 탐지하고 보완할 체계가 부족함.
3. **도구 최적화**: 모든 사이트를 브라우저로 띄우는 것은 비효율적이며, 상황에 맞는 최적의 도구(Trafilatura vs Firecrawl vs Playwright) 선택이 필요함.

## 🎯 요구사항 (Requirements)

### 1. [Pollution Control] 시맨틱 노이즈 및 오염 물질 제거
- **Wiki 특화 정제**: 나무위키/위키피디아 각주(`[1]`, `[2]`), `[편집]`, `[삭제]`, `[[내용]]` 등 위키 문법 완벽 제거.
- **불필요한 기호 제거**: 의미 없는 특수문자 반복, 빈 링크(`[]()`), 비가시 제어 문자 정규식 처리.
- **구조적 정제**: 내용 없는 빈 표(Empty Table), 네비게이션 박스(Navbox) 제외.

### 2. [Format] 고품질 Markdown 추출 (Firecrawl 중심)
- **Semantic Structure**: 문서의 계층 구조(`#`, `##`, `|`)를 시맨틱하게 보존하는 'LLM-Ready Markdown' 확보.
- **Primary Advanced Tool**: 복잡한 레이아웃 대응을 위해 **Firecrawl**을 최우선 고급 스크래퍼로 활용.

### 3. [Fallback Trigger] '부실한 결과물' 정의
다음 조건 중 하나라도 해당하면 즉시 2차(Firecrawl/Playwright)로 전환:
- **Min Length**: 본문 길이 300자 미만.
- **JS Blocked**: "JavaScript를 활성화해주세요", "Cloudflare 차단" 등의 키워드 감지.
- **Structure Failure**: 제목(`h1`, `h2`)이나 단락(`p`) 구조가 거의 없는 단순 나열.
- **Empty Metadata**: 제목(Title) 등 핵심 메타데이터 누락.

### 4. [Tooling] 확장 가능한 인터페이스 구조
- **Scraper Interface**: `Trafilatura`, `Firecrawl`, `Playwright`를 일관된 방식으로 호출하는 Interface 패턴 적용.
- **Playwright Fallback**: Firecrawl로 해결 안 되는 특수 사이트(커스텀 클릭 등 필요)를 위한 PlaywrightScraper 확장성 유지.

## ✅ Definition of Done
1. **Pollution Free**: 위키 노이즈 및 구문 파편이 95% 이상 제거된 마크다운 생성.
2. **Intelligent Fallback**: 4가지 트리거 조건에 따라 자동으로 Firecrawl 전환 검증.
3. **Comparison Utility**: 동일 URL(CLI 입력)에 대해 두 스크래퍼의 결과를 독립된 파일(.md, .txt 등)로 생성하여 사용자가 직접 비교할 수 있는 도구 구현.
4. **Test Pass**: 단위/통합 테스트 100% 통과.
