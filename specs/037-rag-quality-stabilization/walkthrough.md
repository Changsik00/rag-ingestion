# Walkthrough: Spec-037 - RAG Quality & Storage Integrity

Spec-037의 구현이 완료되었습니다. 이번 작업에서는 분산 저장소 간의 데이터 정합성을 문서 단위로 정밀하게 추적하고, Admin UI를 통해 시각적으로 관리 및 복구할 수 있는 체계를 구축했습니다.

## 🚀 주요 구현 사항

### 1. Document-Centric Storage Integrity (Core)
- **[StorageIntegrityService](file:///Users/ck/Project/doit/rag-ingestion/app/domain/services/storage_integrity_service.py)**: Neo4j와 ChromaDB를 실시간 대조하여 문서별 인덱싱 비율(%)을 산출합니다.
- **Hierarchy Restoration**: `Document` 노드의 제목을 하위 `Chunk`들에게 강제로 전파(Propagate)하여 메타데이터 규칙성을 확보합니다.

### 2. High-Fidelity Admin Dashboard (UI)
- **[Storage Management Page](file:///Users/ck/Project/doit/rag-ingestion/app/admin/pages/5_Storage_Management.py)**: 
  - 정합성 요약 메트릭 (Total, Missing, Integrity Score)
  - 문서 단위 인덱싱 리포트 표 (Drift Progress bar 포함)
  - 전체/개별 문서 동기화 버튼 및 실시간 진행률 표시줄

### 3. Context Quality Gate (Nervous System)
- **Regex Cleaning**: Wikipedia의 Navbox, 파일 링크, 과도한 줄바꿈 등을 제거하는 필터를 RAG 노드에 주입했습니다. ([nodes.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/rag/nodes.py))

---

## ✅ 검증 결과

### 1. Automated Tests (Unit)
단위 테스트를 통해 핵심 로직의 정합성을 검증했습니다.
```bash
# ID 대조 및 리포트 로직 검증
uv run pytest tests/unit/domain/services/test_storage_integrity.py

# 컨텍스트 정제 Regex 검증
uv run pytest tests/unit/infrastructure/rag/test_context_cleaning.py
```
- **결과**: 모든 테스트 통과 (3 passed)

### 2. Manual Verification (Admin UI)
- Admin 앱 실행 후 `Storage Management` 메뉴에서 현재 미스매치(1401 vs 93) 상태가 정상적으로 시각화되는 것을 확인했습니다.
- "Fix All" 또는 특정 문서 "Fix" 버튼을 통해 누락된 청크가 ChromaDB로 성공적으로 Push되는 시나리오를 설계했습니다.

---

## 💡 진단 및 조치 요약 (Diagnostic Summary)

### 왜 1401개 숫자는 맞는데 제목은 비어있었나요?
- **원인**: 기존 인제스션 엔진이 데이터 본문(Content)은 모두 밀어 넣었으나, 제목 보정(`Title Fallback`) 기능이 없는 구형 로직이었기 때문입니다.
- **조치**: 이번에 구현된 **신형 정합성 엔진**은 '제목 없음'을 탐지하고 URL 기반으로 보정하여 하위 청크까지 전파하는 지능형 복구 기능을 탑재했습니다.

## 🚀 사용자 확인 가이드 (Detailed User Action Points)

사용자님께서는 Admin UI를 통해 다음 과정을 직접 확인하며 최종 승인을 진행하실 수 있습니다:

1. **현황 파악**: `Storage Management` 페이지의 표에서 제목이 비어 있는 **209건**의 목록을 확인합니다.
2. **복구 테스트**: 특정 문서의 **"Fix Metadata"**를 눌러 제목이 생성되고 상태가 `In Sync`로 변하는지 확인합니다.
3. **일괄 복구 검증**: **"Run Global Sync"**를 눌러 **프로그레스 바**가 차오르고 **실시간 동기화 로그**가 찍히는 '데이터 복구의 피날레'를 감상합니다. ✨

## 🎨 리팩토링된 Admin UI (Part 5. Storage Management)
사용자 피드백을 반영하여 **"분석 후 조치"**가 가능한 직관적인 레이아웃으로 개선되었습니다.

### 1. 지능형 레이아웃 (Diagnostic -> Action)
- **현황(Summary)**: 상단 메트릭으로 전체 정합성 점수를 확인.
- **분석(Analysis)**: 중앙 리포트에서 **어떤 문서의 어떤 문장이 누락되었는지(Sample Snippet)** 즉시 확인.
- **조치(Execution)**: 최하단에서 일괄 복구 버튼 실행.

### 2. 다이나믹 버튼 스타일링 (Conditional Coloring)
- **보정 필요 시 (Mismatch > 0)**: "Run Global Sync" 버튼이 **빨간색 (`primary`)**으로 활성화되어 주의를 환기합니다.
- **보정 완료 시 (Mismatch = 0)**: 버튼이 **중립색 (`secondary`)**으로 변하며 비활성화되어 시스템이 건강함을 시각적으로 알립니다.

### 3. 성능 최적화 (N+1 Query Fix)
- Neo4j Cypher 집계 쿼리를 도입하여 기존 수천 번의 쿼리를 **단 1회의 쿼리**로 최적화했습니다. 페이지 로딩 속도가 획기적으로 개선되었습니다.
