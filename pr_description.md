feat(spec-020): transition to langgraph for ingestion pipeline

## 📋 Summary
<!-- Korean: High-level summary of changes. Use "Before/After" if applicable. -->
Ingestion Pipeline의 오케스트레이션 엔진을 LangChain `RunnableSequence`에서 **LangGraph `StateGraph`**로 전면 교체했습니다.

- **Before**: 선형적인 DAG 구조 (Input -> Extract -> Save). 순환이나 상태 관리가 불가능했습니다.
- **After**: 상태 머신(State Machine) 기반의 Graph 구조. `IngestionState`를 모든 노드가 공유하며, 향후 루프나 조건부 분기를 지원할 수 있는 토대를 마련했습니다.

> 자세한 내용은 [docs/architecture_decisions.md](docs/architecture_decisions.md)를 참고하세요.

## 🎯 Key Review Points
<!-- Korean: Specific areas requiring user attention. -->
1. **IngestionState**: `app/domain/ingestion/state.py`의 구조가 적절한지 확인 부탁드립니다.
2. **Graph Construction**: `app/infrastructure/brain/graph.py`에서 그래프 노드 연결 흐름(`Extract` -> `Validate`)이 의도대로 구현되었는지 검토해 주세요.
3. **Synchronous Node**: 현재 `LLMInterface`가 동기식이라 Node들도 동기(`def`)로 구현되었습니다. 추후 비동기 전환 시 변경 범위가 제한적인지 확인해 주세요.

## 🧪 Verification
### Automated Tests
```bash
# Unit Tests
uv run pytest tests/unit/test_ingestion_state.py
uv run pytest tests/unit/test_graph_nodes.py
uv run pytest tests/unit/test_ingestion_graph.py

# Integration Tests (Success Flow Regression)
uv run pytest tests/integration/bdd/test_success_flows.py
```

### Manual Verification
- 로컬 서버 실행 후 `POST /ingest/web`으로 기사 수집 테스트 완료.
- 로그에서 `extract_metadata` -> `validate_content` 순서로 실행됨을 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/domain/ingestion/state.py`: 파이프라인 상태 정의 (TypedDict)
- `app/infrastructure/brain/nodes.py`: 각 처리 단계(Node) 로직 구현
- `app/infrastructure/brain/graph.py`: StateGraph 구성 및 컴파일 빌더
- `app/infrastructure/brain/adapter.py`: Service Layer와 Graph를 연결하는 어댑터 (`LangGraphAdapter`)
- `docs/architecture_decisions.md`: 아키텍처 결정 기록 (ADR)

### 🛠 Modified Files
- `app/interfaces/api/dependencies.py`: `LangGraphAdapter`를 주입하도록 의존성 설정 변경
- `docs/architecture.md`: ADR 링크 업데이트
- `pyproject.toml`: `langgraph` 의존성 추가

### 🗑 Deleted Files
<!-- Remove section if none -->
- `docs/history/020-decision-record.md`: (Revert) Spec 파일로 내용 복원됨
- `docs/architecture_decisions/001_dag_to_graph_transition.md`: 통합된 파일로 대체됨

**Total:** 8 files changed

## ✅ Definition of Done
- [x] IngestionState TypedDict 정의 및 검증 테스트 통과.
- [x] LangGraph 기반의 IngestionGraph 구현 및 단위 테스트 통과.
- [x] 기존 Integration Test(test_success_flows.py)가 수정 없이(또는 최소 수정으로) 통과.
- [x] 문서화: docs/architecture_decisions.md 및 Spec Update 완료.
