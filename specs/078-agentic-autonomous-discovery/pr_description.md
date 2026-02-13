# feat(spec-078): Autonomous Discovery (Research Crawler)

## 📋 Summary

### 배경 및 목적
사용자가 일일이 URL을 입력하지 않아도, 주제만 주지면 검색 엔진(Google)을 통해 관련 문서를 스스로 탐색하고 수집하는 "능동적 수집" 기능이 필요합니다. 이를 통해 지식 베이스 구축의 자동화 수준을 높입니다.

### 주요 변경 사항
- **Google Search Client**: `app/infrastructure/external_api/google_search_client.py` 구현
- **Discovery Service**: `app/domain/services/discovery_service.py` (BFS Crawling 로직)
- **API Endpoint**: `POST /v1/discovery` (비동기 작업 트리거)
- **LangGraph Tool**: `autonomous_discovery` 툴 구현 (Agent 연동용)
- **Dependencies**: `httpx` (Runtime), `respx` (Test) 추가

## 🎯 Key Review Points
1. **Discovery Logic**: `start_discovery` 메소드 내의 BFS 크롤링 로직 및 Depth 제어
2. **Double Request Strategy**: Discovery 단계에서 `httpx`로 링크를 수집하고, 실제 저장은 `Ingestion.ingest_url`을 호출하여 다시 요청하는 방식의 타당성 (안정성 vs 효율성)
3. **Async Tool**: `DiscoveryTool`의 비동기 실행 및 의존성 주입 방식

## 🧪 Verification

### Automated Tests
```bash
uv run pytest tests/unit/domain/services/test_discovery_service.py tests/unit/interfaces/api/test_discovery_routes.py
```
**테스트 결과 요약:**
- ✅ `test_start_discovery_flow`: 검색 결과 및 링크 크롤링 흐름 검증
- ✅ `test_start_discovery_endpoint`: API 응답 형식 및 서비스 호출 검증

## 📦 Files Changed
### 🆕 New Files
- `app/infrastructure/external_api/google_search_client.py`: Google CSE API Client
- `app/domain/services/discovery_service.py`: Discovery Core Logic
- `app/interfaces/api/v1/endpoints/discovery.py`: Discovery API Endpoint
- `app/interfaces/tools/discovery_tool.py`: LangChain/LangGraph Tool

### 🛠 Modified Files
- `app/core/config.py`: Google API Key 설정 추가
- `app/interfaces/api/dependencies.py`: DI 컨테이너에 서비스 등록
- `pyproject.toml`: 의존성 추가

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
