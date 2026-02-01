# refactor: clean architecture layer refinement (spec 052)

## 📌 개요
Spec 051 이후 식별된 기술 부채를 해결하기 위해, 클린 아키텍처 원칙에 따라 계층 경계 위반을 수정하고, 네이밍 규칙을 표준화했습니다.

## 🛠 주요 변경 사항

### 1. 아키텍처 계층 정제 (Layer Refinement)
- **Interface 이동**: `LLMInterface`, `ScraperInterface`를 `domain`에서 `application/interfaces`로 이동 (Infrastructure와 Application 연결 고리).
- **Service 이동**: `Feedback` 서비스를 `domain`에서 `application/services`로 이동.
- **Value Object 이동**: `DocumentMetadata`를 `domain/models`에서 `domain/value_objects`로 이동.

### 2. 네이밍 및 구조 표준화 (Standardization)
- **Agent**: `admin_agent.py` → `agent.py` (관리자 기능 탈피, 범용화).
- **Service**: `IngestionUseCase` → `Ingestion` 클래스명 변경 (일관성 확보).
- **Core**: `core/utils/` 제거 및 평탄화, `logging_config.py` → `logger.py` 변경.
- **State**: `state.py` → `graph_state.py`로 명확화 (`ingestion`, `rag` 도메인 공통).

### 3. 코드 정리 (Cleanup)
- 레거시 파일 제거: `app/interfaces/api/endpoints/jobs.py` (중복 엔드포인트).
- 전체 Import 구문 업데이트 (약 200+ 라인 수정).

## ✅ 검증
- [x] `uv run pytest` (194개 통과, 60개 skip).
- [x] `uv run ruff check .` (0 오류).
- [x] `uv run ruff format .` (Formatting 완료).

## 📝 영향 범위
- 내부 모듈 경로가 대거 변경되었으므로, 외부 스크립트나 노트북에서 import 경로 수정이 필요할 수 있습니다.
- API 엔드포인트는 변경 없으므로 프론트엔드 영향은 없습니다.
