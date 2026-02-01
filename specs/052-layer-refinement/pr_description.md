# refactor(spec-052): clean architecture layer refinement

## 📋 Summary

### 배경 및 목적
Spec 051 작업 이후, 여전히 남아있는 클린 아키텍처 계층 위반 사항(Domain 계층의 인프라 의존성)과 네이밍 불일치 문제를 해결하기 위함입니다. 이를 통해 각 계층의 책임을 명확히 하고 코드베이스의 일관성을 확보합니다.

### 주요 변경 사항
- [x] **Interface 이동**: `LLMInterface`, `ScraperInterface`를 `domain`에서 `application/interfaces`로 이동 (계층 구조 교정)
- [x] **Service 이동**: `Feedback` 서비스를 `domain`에서 `application/services`로 이동
- [x] **Value Object 이동**: `DocumentMetadata`를 `domain/models`에서, `GraphState`를 `domain/{ingestion,rag}`에서 `domain/value_objects`로 이동 (파일명 `ingestion_state.py`, `rag_state.py`로 변경).
- [x] **네이밍 표준화**: `admin_agent` → `agent`, `IngestionUseCase` → `Ingestion`, `logging_config` → `logger`, `state` → `graph_state`
- [x] **코드 정리**: 중복된 Legacy API 엔드포인트(`app/interfaces/api/endpoints/jobs.py`) 제거

## 🎯 Key Review Points
1. **Layer Dependency**: Domain 계층이 Application/Infrastructure 계층을 의존하지 않는지 확인
2. **Naming Consistency**: 변경된 `agent`, `Ingestion`, `graph_state` 네이밍이 전체 코드베이스에 일관되게 적용되었는지 확인
3. **Module Paths**: 대규모 import 경로 변경이 누락 없이 적용되었는지 확인

## 🧪 Verification

### Automated Tests
```bash
uv run pytest
```
**테스트 결과 요약:**
- ✅ **전체 테스트**: 194개 통과 / 60개 Skip (총 254개)
- ✅ `tests/unit/test_ingestion_top_level_state.py`: 모듈 경로 변경(`graph_state`) 반영 후 통과

### Manual Verification (Scenarios)
1. **Import 검증**: 주요 모듈(`GraphState`, `Ingestion`, `Agent`)의 import가 정상적으로 동작하는지 `uv run python`으로 확인
2. **Lint Check**: `ruff check .` 및 `ruff format .` 수행 시 오류 없음

## 📦 Files Changed

### 🆕 New Files (Renamed/Moved)
- `app/application/interfaces/llm.py`: (from domain)
- `app/application/interfaces/scraper.py`: (from domain)
- `app/application/services/agent.py`: (renamed from admin_agent)
- `app/domain/ingestion/graph_state.py`: (renamed from state)
- `app/core/logger.py`: (renamed from logging_config)

### 🛠 Modified Files
- `app/interfaces/api/dependencies.py`: DI 컨테이너 import 경로 업데이트
- `tests/`: 모든 테스트 코드의 import 경로 업데이트
- 그 외 다수의 파일에서 import 경로 수정

**Total:** 40+ files changed

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
