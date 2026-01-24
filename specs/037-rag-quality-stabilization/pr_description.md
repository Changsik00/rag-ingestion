# feat(spec-037): RAG 저장소 정합성 및 관리자 대시보드 고도화

## 📋 Summary
분산 저장소(Neo4j, ChromaDB) 간의 데이터 불일치를 해결하고 검색 품질을 안정화하기 위한 **'저장소 정합성 관리 시스템'**을 구축했습니다. 단순히 개수를 맞추는 것을 넘어, 문서 계층 구조를 활용한 메타데이터 보정과 노이즈 정제 필터를 통합했습니다.

- **Before**: 데이터 누락 여부를 확인하기 어렵고, 위키피디아 노이즈 및 메타데이터 부재로 검색 품질 저하.
- **After**: Admin UI에서 실시간으로 정합성을 모니터링하고, 누락된 데이터 및 깨진 메타데이터를 시각화하여 즉시 복구 가능.

## 🎯 Key Review Points
1. **Source of Truth (Neo4j) 원칙**: Neo4j의 `Document`와 `Chunk`를 기준으로 ChromaDB 인덱스를 동기화하는 전략을 수립했습니다.
2. **Hierarchical Metadata Sync**: 상위 문서의 제목이 없는 경우 보정하고, 이를 하위 청크까지 전파(`Propagate`)하여 데이터 일관성을 확보했습니다.
3. **Live UI Feedback**: Streamlit의 `st.progress`와 `st.status`를 활용하여 동기화 과정을 실시간으로 추적 가능하게 했습니다.
4. **Context Quality Gate**: RAG 추론 노드에 위키피디아 전용 정규식 필터를 주입하여 답변 방해 요소(Navbox, Infobox 등)를 원천 차단했습니다.

## 🧪 Verification
### Automated Tests
```bash
# ID 대조 및 리포트 로직 검증
uv run pytest tests/unit/domain/services/test_storage_integrity.py

# 컨텍스트 정제 Regex 검증
uv run pytest tests/unit/infrastructure/rag/test_context_cleaning.py
```

### Manual Verification (USER CHECK REQUIRED) 🚀
사용자님께서 직접 확인하셔야 할 **핵심 동작**입니다:
1. **Admin 실행**: `streamlit run app/admin/Overview.py` 실행 후 **`5_Storage_Management`** 페이지 접속.
2. **현황 파악**: `Integrity Score`와 `Document Drift Report` 표에서 현재 제목이 비어 있는 **209건**의 목록 확인.
3. **복구 버튼 클릭**: 상단의 **"Run Global Sync"** 또는 특정 문서의 **"Fix"** 버튼 클릭.
4. **실시간 피드백**: **프로그레스 바**가 차오르고 하단에 **"Synced X / 209 items"** 로그가 실시간으로 변하는지 확인.
5. **최종 확인**: 작업 완료 후 모든 `Status`가 **'In Sync'**로 변하고 제목이 보정되었는지 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/domain/services/storage_integrity_service.py`: 정합성 분석 및 보정 핵심 엔진
- `app/admin/services/integrity_service.py`: Admin UI 전용 서비스 래퍼
- `app/admin/pages/5_Storage_Management.py`: 관리자 정합성 대시보드 페이지
- `tests/unit/domain/services/test_storage_integrity.py`: 서비스 단위 테스트
- `tests/unit/infrastructure/rag/test_context_cleaning.py`: 노이즈 필터 단위 테스트

### 🛠 Modified Files
- `app/domain/interfaces/document_repository.py`: ID 일괄 조회를 위한 인터페이스 확장
- `app/infrastructure/storage/neo4j_document_repository.py`: Neo4j 전용 ID 조회 및 이중 저장 로직 강화
- `app/infrastructure/storage/chroma.py`: ChromaDB 전용 ID 조회 로직 추가
- `scripts/sync_indices.py`: UI 엔진을 활용한 CLI 스크립트 고도화
- `app/infrastructure/rag/nodes.py`: RAG 추론 단계에 노이즈 클리닝 게이트 주입

**Total:** 10 files changed

## ✅ Definition of Done
- [x] Neo4j vs ChromaDB 실시간 개수 대조 가능
- [x] 문서 단위 인덱싱 리포트 및 진행률 시각화
- [x] 제목 부재 문서 자동 보정 및 전파 (Title Fallback & Propagation)
- [x] 위키피디아 노이즈 정제 로직 RAG 통합
- [x] 모든 단위 테스트 Pass
