# feat(spec-038): structural decoupling of admin ui and async core alignment

## 📋 Summary
기존 `app/admin`에 위치하여 백엔드와 강하게 결합되어 있던 관리자 UI를 `admin/` 디렉토리로 물리적으로 완전히 분리하고, 모든 통신을 전용 API 레이어를 통해 수행하도록 변경했습니다. 또한, 이 과정에서 발생하는 비동기 정합성 문제를 해결하기 위해 인제스천 및 RAG 코어 엔진을 완전 비동기(`async/await`) 구조로 정착시켰습니다.

## 🎯 Key Review Points
1. **Thin Client 전환**: `admin/` 내에서 `app.*` import가 완전히 제거되었으며, `api_client`를 통해서만 데이터가 흐르는지 확인 부탁드립니다.
2. **비동기 코어 엔진**: `IngestionNodes`, `RAGNodes` 등이 `async`로 전환되었으며, LLM 호출 시 `await` 처리가 누락된 곳이 없는지 검토가 필요합니다.
3. **API 추상화**: 관리자 전용 API(`/api/v1/admin`)가 기존 UI의 기능을 모두 수용하며 적절하게 정의되었는지 확인 부탁드립니다.

## 🧪 Verification
### Automated Tests
```bash
uv run pytest . -v
# 207 passed, 0 failures (11 skipped due to missing API keys)
```

### Manual Verification
1. `rag-admin` 컨테이너 실행 후 백엔드 서버와의 API 연동 확인.
2. RAG Playground에서 질문 던진 후 Trace 및 HITL 기능 작동 확인.
3. Storage Management에서 Drift Report 생성 및 데이터 동기화 기능 확인.

## 📦 Files Changed

### 🆕 New Files
- `admin/utils/api_client.py`: Streamlit용 전용 HTTP API 클라이언트.
- `app/interfaces/api/v1/endpoints/admin/`: 관리자 전용 API 컨트롤러 (storage, rag, jobs, graph).
- `specs/038-structural-decoupling/walkthrough.md`: 상세 아키텍처 및 검증 결과 문서.

### 🛠 Modified Files
- `app/main.py`: 관리자용 API 라우터 등록.
- `admin/`: 기존 `app/admin`에서 이동된 파일들. 모든 직접 import를 API 기반으로 수정.
- `app/infrastructure/brain/nodes.py`: `extract_metadata` 등 인제스천 노드 비동기화.
- `app/infrastructure/rag/nodes.py`: RAG 파이프라인 노드 비동기화 및 `await` 적용.
- `app/domain/services/`: `IntentClassifier`, `QueryRewriter` 비동기 메서드로 전환.
- `tests/`: 단위/통합 테스트 비동기 대응 및 `AsyncMock` 적용.

### 🗑 Deleted Files
- `app/admin/`: 물리적 디렉토리 이동으로 인한 기존 위치 삭제.

**Total:** 50+ files changed (including moved admin files and updated tests)

## ✅ Definition of Done
- [x] Admin UI에서 백엔드 직접 import 완벽 제거 (Zero Import)
- [x] 관리자 전용 API 15개 이상 정상 동작 확인
- [x] 전체 테스트 슈트(207개) 통과 및 정합성 검증 완료
- [x] 상세 Walkthrough 문서 작성 및 PR 명세 최신화 완료
