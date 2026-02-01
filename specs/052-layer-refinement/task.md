# 작업 목록: Spec 052 - Clean Architecture 계층 정제

## 진행 상황
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트
- [x] 사용자 계획 승인

---

## Task 1: 인터페이스 계층 마이그레이션 (P1 - 높음)

### 1-1. LLM 인터페이스를 Application 계층으로
- [x] **디렉토리 생성**: `app/application/interfaces/` (없는 경우)
- [x] **이동**: `app/domain/interfaces/llm.py` → `app/application/interfaces/llm.py`
- [x] **Import 찾기**: `grep -r "from app.domain.interfaces.llm" app/ tests/`
- [x] **업데이트**: 모든 import 문 (~15개 파일)
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `refactor(layer): move llm interface to application layer (Spec 052)`

### 1-2. Scraper 인터페이스를 Application 계층으로
- [x] **이동**: `app/domain/interfaces/scraper.py` → `app/application/interfaces/scraper.py`
- [x] **업데이트**: 모든 import (~8개 파일)
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `refactor(layer): move scraper interface to application layer (Spec 052)`

### 1-3. Feedback 서비스를 Application 계층으로
- [x] **이동**: `app/domain/services/feedback.py` → `app/application/services/feedback.py`
- [x] **테스트 이동**: `tests/unit/domain/services/test_feedback.py` → `tests/unit/application/services/test_feedback.py` (존재 시)
- [x] **업데이트**: 모든 import (~10개 파일)
- [x] **업데이트**: `dependencies.py`의 의존성 주입
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `refactor(layer): move feedback service to application layer (Spec 052)`

---

## Task 2: Value Object 재정리 (P1 - 높음)

### 2-1. DocumentMetadata를 Value Objects로
- [x] **이동**: `app/domain/models/document_metadata.py` → `app/domain/value_objects/document_metadata.py`
- [x] **업데이트**: 모든 import (~20개 파일)
- [x] **정리**: `app/domain/models/` 비어있으면 제거
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `refactor(vo): move DocumentMetadata to value_objects (Spec 052)`

---

## Task 3: 네이밍 일관성 (P2 - 중간)

### 3-1. Admin Agent → Agent
- [x] **파일 이름 변경**: `app/application/services/admin_agent.py` → `app/application/services/agent.py`
- [x] **테스트 이름 변경**: `tests/unit/application/services/test_admin_agent.py` → `test_agent.py` (존재 시)
- [x] **업데이트**: 모든 import (~12개 파일)
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `refactor(naming): rename admin_agent to agent (Spec 052)`

### 3-2. IngestionUseCase → Ingestion
- [x] **클래스 이름 변경**: `app/application/services/ingestion.py`에서 `IngestionUseCase` → `Ingestion`
- [x] **테스트 이름 변경**: `tests/unit/test_ingestion_use_case.py` → `tests/unit/application/services/test_ingestion.py`
- [x] **업데이트**: 모든 클래스 참조 (~25개 파일)
- [x] **업데이트**: 의존성 주입
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `refactor(naming): rename IngestionUseCase to Ingestion (Spec 052)`

### 3-3. Core 파일 단순화
- [x] **이동**: `app/core/utils/file_processor.py` → `app/core/file_processor.py`
- [x] **이름 변경**: `app/core/logging_config.py` → `app/core/logger.py`
- [x] **업데이트**: 모든 import (~15개 파일)
- [x] **정리**: `app/core/utils/` 디렉토리 제거
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `refactor(core): simplify core structure and naming (Spec 052)`

---

## Task 4: State 객체 정제 (P3 - 낮음)

### 4-1. State 파일 이름 변경
- [x] **이름 변경**: `app/domain/ingestion/state.py` → `app/domain/ingestion/graph_state.py`
- [x] **이름 변경**: `app/domain/rag/state.py` → `app/domain/rag/graph_state.py`
- [x] **업데이트**: 모든 import (~10개 파일)
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `refactor(naming): rename state files to graph_state for clarity (Spec 052)`

---

## Task 5: 중복 파일 정리 (P3 - 낮음)

### 5-1. 중복 파일 찾기 및 제거
- [x] **조사**: `find app/interfaces/api -name "*.py" | sort`
- [x] **검증**: `app/interfaces/api/endpoints/jobs.py`가 `v1/endpoints/jobs.py`와 중복인지 확인
- [x] **제거**: 중복 확인 시 삭제
- [x] **테스트**: `uv run pytest`
- [x] **커밋**: `chore(cleanup): remove duplicate endpoint files (Spec 052)`

---

## Task N: 최종 검증 및 PR

- [x] **Lint 확인**: `uv run ruff check .` (0 오류)
- [x] **Format 확인**: `uv run ruff format --check .`
- [x] **전체 테스트**: `uv run pytest` (194+ 통과)
- [x] **문서화**: walkthrough.md 작성
- [x] **문서화**: pr_description.md 작성
- [x] **커밋**: `docs(spec-052): archive walkthrough and pr description`
- [x] **PR 생성**: 리뷰 요청
