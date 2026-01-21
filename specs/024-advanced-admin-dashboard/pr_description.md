feat(spec-024): advanced admin dashboard

## 📋 Summary
본 PR은 RAG Ingestion 파이프라인의 관측성과 제어 권한을 강화하기 위한 **Advanced Admin Dashboard (Spec 024)**를 구현합니다.
Spec 024에서 정의된 4가지 핵심 기능을 중심으로 관리자 도구를 대폭 개선하였습니다.

**주요 구현 내용:**
1. **Graph Explorer (지식 그래프 탐색)**:
    - Neo4j 데이터를 시각화하여 직관적으로 탐색.
    - 초보자를 위한 **Query Helper** (Preset 및 Drop-down Query Builder) 제공.
2. **HITL Control Center (Human-in-the-Loop 제어)**:
    - 에이전트의 현재 상태(**Live Status**)를 모니터링.
    - `interrupt` 상태의 스레드를 조회하고, 관리자 피드백과 함께 **Resume** 할 수 있는 제어 패널.
3. **Reasoning Trace Viewer (추론 과정 추적)**:
    - LangGraph의 실행 트레이스를 추적하고, 에이전트의 상태 변화(State Snapshot)를 상세 JSON으로 검사.
4. **RAG Playground (검색 품질 검증)**:
    - 실제 검색 엔진(ChromaDB)을 활용한 질의응답 테스트 환경.
    - 검색 품질에 대한 **Feedback (좋아요/싫어요)** 수집 기능 통합.

## 🎯 Key Review Points
1. **Backend Refactoring (`adapter.py`, `jobs.py`)**: `LangGraphAdapter`에 `SqliteSaver`를 주입하여 상태 영속성을 확보한 방식과 API 엔드포인트 설계가 적절한지 검토 부탁드립니다.
2. **Interface Protocol (`DocumentRepository`)**: `search(query, limit)` 메서드를 인터페이스에 추가하고 `ChromaStorage`(구현)와 `Neo4jStorage`(미구현/빈리스트)에 반영한 구조적 변경 사항을 확인해 주세요.
3. **Streamlit UI**: 각 페이지(`1_Graph_Explorer`, `2_HITL_Control` 등)의 상호작용 로직과 예외 처리(특히 JSON 파싱 등)가 견고한지 검토 바랍니다.

## 🧪 Verification

### 1. Docker 환경 재시작 (권장)
변경 사항이 반영된 환경을 구성하기 위해 컨테이너를 재빌드 및 실행합니다.
```bash
docker compose down
docker compose up --build -d
```
> `-d` 옵션 제거 시 로그 확인 가능

### 2. 접속 및 수동 검증
브라우저에서 **[http://localhost:8501](http://localhost:8501)** 에 접속하여 다음 항목을 확인합니다.

1. **🕸️ Graph Explorer**:
    - 사이드바 > **Graph Explorer** 선택.
    - **Preset Queries**에서 "All Persons" 선택 후 `Run Query` 클릭 → 그래프 렌더링 확인.
2. **🎮 RAG Playground**:
    - 사이드바 > **RAG Playground** 선택.
    - 키워드(예: "RAG") 입력 후 검색 결과(Retrieved Context) 및 답변 생성 확인.
    - 👍 / 👎 버튼 클릭 시 `Toast` 메시지 확인 (피드백 저장).
3. **🚦 HITL Control**:
    - 사이드바 > **HITL Control** 선택.
    - 활성 스레드 목록 조회 및 `interrupted` 스레드 Resume 동작 확인.

### Automated Tests
```bash
# Unit Tests
uv run pytest tests/unit/admin/test_graph_service.py
uv run pytest tests/unit/admin/test_hitl_service.py
uv run pytest tests/unit/admin/test_feedback_service.py

# Full Suite
uv run pytest
```

## 📦 Files Changed

### 🆕 New Files
- `app/admin/dashboard.py`: Streamlit 메인 엔트리 포인트.
- `app/admin/config.py`: Neo4j 등 관리자 설정 파일.
- `app/admin/services/*.py`: Graph, HITL, Feedback 비즈니스 로직 서비스.
- `app/admin/pages/*.py`: Graph Explorer, HITL Control, Trace Viewer, RAG Playground UI 파일.
- `tests/unit/admin/*.py`: 각 서비스에 대한 단위 테스트.

### 🛠 Modified Files
- `app/infrastructure/brain/adapter.py`: `SqliteSaver` 지원 및 `list_threads`, `get_state`, `resume` 메서드 추가.
- `app/interfaces/api/endpoints/jobs.py`: HITL 관련 API(`.active/threads`, `.trace`, `.resume`) 추가.
- `app/domain/interfaces/document_repository.py`: `search` 추상 메서드 추가.
- `app/infrastructure/storage/*.py`: `ChromaStorage`에 벡터 검색 구현, `Neo4jStorage`에 빈 구현 추가.
- `pyproject.toml`: `streamlit`, `plotly` 등 의존성 추가.

**Total:** 16 files changed

## ✅ Definition of Done
- [x] Spec 024에 정의된 4가지 핵심 기능(Graph, HITL, Trace, Playground) 구현 완료
- [x] 모든 Backend Service에 대한 단위 테스트 작성 및 통과
- [x] `ruff` 린트 및 포맷팅 통과
- [x] E2E 수동 검증 및 Walkthrough 문서 작성 완료
