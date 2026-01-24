# feat(spec-034): rag pipeline recovery and stability

## 📋 Summary
기존 RAG 파이프라인(Spec 033)에서는 특정 대상을 지목할 때 DB 필터링 조건이 너무 엄격하여 검색 결과가 0건으로 나오는 현상(**Strict Filtering Issue**)과, 정보가 없음에도 LLM이 아는 척 답변하는 현상(**Hallucination Risk**)이 있었습니다. 또한 Admin Playground에서 대화 도중 서버가 재시작되거나 세션이 바뀌면 대화 내역이 유실되는 불편함이 있었습니다.

이번 작업에서는 이를 해결하기 위해 다음의 3가지 핵심 개선을 수행했습니다:
1. **Adaptive Retrieval (Fallback)**: 필터링 검색 실패 시 자동으로 범위를 넓혀 재검색하여 사용자에게 유의미한 정보를 반드시 제공하도록 개선했습니다.
2. **Deterministic Guardrails**: 프롬프트를 강화하여 컨텍스트에 없는 내용은 명확히 "모른다"고 답하게 하여 시스템 신뢰도를 높였습니다.
3. **Session Persistence (Hotfix)**: Playground에 `AsyncSqliteSaver` 체크포인터를 완벽히 연동하여 대화 내역과 내부 상태(State)가 영구적으로 보존되도록 안정화했습니다. (`aiosqlite` 기반 비동기 처리 도입)

## 🎯 Key Review Points
1. **Automatic Fallback Mechanism**: `retrieve_hybrid` 노드에서 `if not results and filters: ... retry without filters` 로직의 적절성.
2. **Prompt Instruction Clarity**: LLM에게 부여된 `CRITICAL RULES`가 실제 할루시네이션을 억제하기에 충분히 강력한지 검토.
3. **Async Checkpointer Stability**: `dependencies.py`에서 `AsyncSqliteSaver`를 싱글톤으로 관리하고 `aiosqlite`를 사용하도록 변경한 구조의 적절성.
4. **UI Feedback**: Fallback 발생 시 사용자에게 노란색 경고 창으로 상태를 고지하는 UX 흐름.

## 🧪 Verification
### Automated Tests
```bash
# Fallback 및 Prompt 단위 테스트 실행
uv run pytest tests/unit/infrastructure/rag/test_rag_nodes.py -v

# 체크포인터 및 HITL 연동 테스트
uv run pytest tests/integration/bdd/test_human_loop.py

# 전체 통합 테스트 (204 passed)
uv run pytest -v
```

### Manual Verification (Admin Dashboard 테스트 시나리오)

#### Scenario 1: Strict Filter Fallback (실패 방지 테스트)
1. **상황**: "스티브 잡스"라는 문서가 DB에 있지만, 사용자가 실수로 "Jobs"라는 키워드 필터를 건 경우.
2. **방법**: Playground 사이드바의 `Select Documents`에서 아무 문서나 하나 선택(고정)하고, 그 문서와 전혀 상관없는 질문을 던집니다.
3. **결과**: 예전 같으면 "정보가 없다"고 나오거나 오류가 났겠지만, 이제는 **"🔄 Fallback Triggered"** 경고 박스가 상단에 뜨면서 전역 검색 결과로 올바른 답변을 생성해야 합니다.

#### Scenario 2: Hallucination Guard (아는 척 방지 테스트)
1. **상황**: 지식 베이스에 전혀 없는 생소한 개념(예: "초전도체 외계인 이론")에 대해 질문.
2. **방법**: 사이드바 필터를 모두 해제하고 위 질문을 던집니다.
3. **결과**: LLM이 지어내지 않고, **"제 지식 베이스에 해당 정보가 충분하지 않아 답변드리기 어렵습니다."** 계열의 정중한 거절 메시지를 출력해야 합니다.

#### Scenario 3: Persistence Check (대화 보존 테스트)
1. **상황**: 대화 도중 브라우저를 새로고침하거나 서버를 재시작.
2. **방법**: 질문을 한 번 주고받은 뒤, Playground 화면을 새로고침합니다.
3. **결과**: 이전 대화 내역이 그대로 남아있어야 하며, 디버그UI 우측 상단의 사고 과정(Reasoning Trace)도 복구되어야 합니다.

## 📦 Files Changed

### 🆕 New Files
- `specs/034-rag-pipeline-recovery/spec.md`: 요구사항 정의서
- `specs/034-rag-pipeline-recovery/plan.md`: 실행 계획서
- `specs/034-rag-pipeline-recovery/task.md`: 태스크 작업 목록
- `specs/034-rag-pipeline-recovery/walkthrough.md`: 작업 결과 기술서
- `specs/034-rag-pipeline-recovery/pr_description.md`: PR 본문 (현재 파일)

### 🛠 Modified Files
- `app/infrastructure/rag/nodes.py`: Fallback 로직 및 프롬프트 가드레일 구현
- `app/admin/pages/4_RAG_Playground.py`: `AsyncSqliteSaver` 핸들링 및 디버그 UI 연동
- `app/interfaces/api/dependencies.py`: `AsyncSqliteSaver` 싱글톤 의존성 주입 (Hotfix)
- `app/domain/rag/state.py`: `fallback_triggered` 필드 추가
- `pyproject.toml`: `aiosqlite` 의존성 추가
- `docs/architecture/rag_pipeline.md`: 트러블슈팅 해결책 업데이트
- `docs/guides/admin_guide.md`: Playground 가이드 업데이트
- `tests/unit/infrastructure/rag/test_rag_nodes.py`: 단위 테스트 추가

**Total:** 12 files changed

## ✅ Definition of Done
- [x] 필터 검색 실패 시 자동 Fallback 및 시각화 확인
- [x] Empty Context 상황에서 할루시네이션 방지 프롬프트 작동 확인
- [x] Playground 대화 내역(Session) 보존 확인
- [x] 전체 린트 및 통합 테스트(204개) 통과
