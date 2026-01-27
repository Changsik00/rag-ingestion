# Walkthrough - Spec 043: Robust Ingestion

## 1. Changes
`ChromaStorage.save_chunks` 메서드가 한 번에 모든 청크를 저장하던 방식에서, `AdminConfig.CHROMA_BATCH_SIZE` (Default: 20) 설정에 따라 배치 단위로 나누어 저장하도록 변경되었습니다.

### 주요 변경 파일
- `app/core/config.py`: `CHROMA_BATCH_SIZE` 설정 추가
- `app/infrastructure/storage/chroma.py`: Batch Processing 및 Retry Logic 구현

## 2. Verification Results

### Automated Test
`scripts/test_robust_ingestion.py`를 통해 50개의 청크가 3개의 배치(20, 20, 10)로 나뉘어 저장되는지 검증했습니다.

```bash
$ uv run python scripts/test_robust_ingestion.py

2026-01-27 23:38:27,959 - app.infrastructure.storage.chroma - INFO - Saving batch 1/3 (20 chunks)...
2026-01-27 23:38:27,960 - app.infrastructure.storage.chroma - INFO - Saving batch 2/3 (20 chunks)...
2026-01-27 23:38:27,960 - app.infrastructure.storage.chroma - INFO - Saving batch 3/3 (10 chunks)...

✅ Verification Passed: 50 chunks were saved in 3 batches (20, 20, 10).
```

## 3. Conclusion
대형 문서(수백 개 청크) 수집 시 API Timeout이나 Payload Limit 문제를 방지하고, 안정적인 저장이 가능해졌습니다.
