# feat(spec-043): robust ingestion with chroma batching

## 📋 Summary

### 배경 및 목적
기존 `ChromaStorage`는 모든 청크를 한 번의 API 호출로 저장(`collection.add`)하도록 구현되어 있었습니다. 이로 인해 청크가 많은 대형 문서(예: '일론 머스크' 위키백과, 청크 ~159개) 수집 시:
- ❌ **API Timeout**: Gemini Embedding API 또는 ChromaDB 처리 시간 초과
- ❌ **Payload Limit**: 한 번에 전송하는 데이터 크기 초과
- ❌ **Data Consistency**: Neo4j에는 저장되었으나 Chroma에는 저장되지 않는 문제 발생

이를 해결하기 위해 **Robust Ingestion (Spec 043)**을 통해 배치 처리 로직을 도입했습니다.

### Before (Single Batch)
```python
def save_chunks(self, chunks: list[Chunk]) -> None:
    # 모든 청크를 한 번에 저장
    self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
```

### After (Batch Processing)
```python
def save_chunks(self, chunks: list[Chunk]) -> None:
    # BATCH_SIZE(20) 단위로 나누어 순차 저장
    for i in range(0, total_chunks, self.batch_size):
        batch = chunks[i : i + self.batch_size]
        self.collection.add(ids=batch_ids, ...)
        logger.info(f"Saving batch {current}/{total}...")
```

### 주요 변경 사항
1.  **Configuration**: `AdminConfig` 및 `app/core/config.py`에 `CHROMA_BATCH_SIZE` (Default: 20) 추가
2.  **Infrastructure**: `ChromaStorage.save_chunks` 리팩토링 (Batch Loop + Retry Logic)
3.  **Logging**: 배치 진행 상황 로깅 추가로 모니터링 강화

## 🎯 Key Review Points
1.  **Batch Size**: 20으로 설정된 `CHROMA_BATCH_SIZE`가 적절한지 (너무 작으면 오버헤드, 너무 크면 타임아웃)
2.  **Retry Logic**: 배치 단위 실패 시 3회 재시도(Exponential Backoff) 로직의 적절성

## 🧪 Verification

### Automated Tests
```bash
# Unit Tests (Mock 기반 Batch 로직 검증)
uv run pytest scripts/test_robust_ingestion.py -v
# ✅ 결과: 1 passed (50개 청크 -> 3회 배치 호출 검증 완료)
```
- 50개의 더미 청크 생성
- `CHROMA_BATCH_SIZE=20` 설정
- `collection.add`가 3번(20, 20, 10) 호출되는지 확인

### Manual Verification
- Walkthrough Artifact: [walkthrough.md](walkthrough.md)

## ✅ Definition of Done
- [x] `AdminConfig`에 `CHROMA_BATCH_SIZE` 설정 추가
- [x] `ChromaStorage` 리팩토링 및 Unit Test 작성
- [x] 대형 문서 수집 시나리오 검증 스크립트(`scripts/test_robust_ingestion.py`) 통과
- [x] Code Quality Check (`ruff check`, `ruff format`) 완료
