# feat(spec-064): rag observability dashboard

## 📋 Summary

### 배경 및 목적
RAG 파이프라인의 실행 과정이 블랙박스로 남아있어 디버깅과 성능 분석이 어렵습니다. Intent 분류, 검색, 리랭킹, 생성 등 각 단계의 상세 로그와 메트릭(Latency, Token)을 시각화하기 위해 **LangFuse**를 도입합니다.

### 주요 변경 사항
- [x] **Infra**: `langfuse` 패키지 추가 및 `LangfuseCallbackHandler` Helper 구현.
- [x] **Service**: `rag.py` 및 `rag_nodes.py`에 Callback Handler 주입 및 전파 로직 추가.
- [x] **UI**: Admin RAG Playground에 LangFuse Trace 페이지로 이동하는 Deep Link 버튼 추가.
- [x] **Docs**: `docs/features/observability.md` 아키텍처 문서 추가 (Async Batch 매커니즘 설명 포함).

## 🎯 Key Review Points
1.  **Callback Injection**: `app/application/services/rag.py`에서 `LangfuseCallbackHandler`를 생성하여 `graph.ainvoke(config=...)`로 주입하는 방식.
2.  **Robustness**: LangFuse API Key가 없거나 연결 실패 시에도 RAG 서비스가 죽지 않고 Graceful Fallback 처리되는지 (`langfuse_helper.py`).
3.  **Communication Mechanism**: 웹소켓이 아닌 비동기 HTTP 배치(Fire-and-Forget) 방식을 사용함에 대한 이해.

## 🧪 Verification

### Automated Tests
```bash
uv run pytest
```
**테스트 결과 요약:**
- ✅ 기존 RAG Node 테스트 42개 전수 통과 (인터페이스 변경 호환성 확인).

### Manual Verification (Scenarios)

#### 1. 환경 설정 (LangFuse Key)
오류 상황(키 없음)과 정상 상황(키 있음)을 모두 테스트합니다.

**시나리오 A: API Key 미설정 (Graceful Failure)**
1. `.env` 파일의 `LANGFUSE_SECRET_KEY` 값을 주석 처리하거나 임시로 변경합니다.
2. `admin/Home.py` 실행: `uv run streamlit run admin/Home.py`
3. **RAG Playground** 메뉴로 이동하여 질문을 입력합니다.
4. **확인 포인트**:
   - 답변이 에러 없이 정상 생성되는지 확인.
   - 터미널 로그에 `LangFuse environment variables not set` 경고가 뜨는지 확인.
   - 답변 하단에 "View Trace" 버튼이 **없어야 함**.

**시나리오 B: API Key 설정 (Normal Operation)**
1. `.env` 파일에 정상적인 LangFuse 키를 입력합니다.
2. Streamlit 재실행 (또는 Rerun).
3. **RAG Playground**에서 질문 입력.
4. **확인 포인트**:
   - 답변 생성 완료 후, 답변 영역 하단에 **[🔍 View Trace in LangFuse]** 링크 버튼이 나타나는지 확인.
   - 버튼 클릭 시 LangFuse(Cloud 또는 Local) 웹페이지로 이동하여 해당 질문의 **Trace 상세 화면**이 열리는지 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/infrastructure/monitoring/langfuse_helper.py`: LangFuse Handler 팩토리.
- `docs/features/observability.md`: 아키텍처 문서.

### 🛠 Modified Files
- `pyproject.toml` (+langfuse dependency)
- `app/application/services/rag.py` (+callback injection)
- `app/infrastructure/ai/rag_nodes.py` (+runnable config propagation)
- `admin/pages/4_RAG_Playground.py` (+view trace button)

**Total:** 6 files changed

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
