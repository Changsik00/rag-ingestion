# Implementation Plan: Spec 043 - Robust Ingestion (Chroma Batching)

## 📋 Branch Strategy
- `feat/spec-043-robust-ingestion`

## 🛑 User Review Required

> [!IMPORTANT]
> **Batch Size 결정**: 기본값을 `20`으로 설정합니다. 이는 Gemini Embedding API 및 일반적인 Vector DB의 안정적인 처리량을 고려한 값입니다. 추후 성능 튜닝이 필요하면 `env`로 조절 가능합니다.

**검토 필요 사항:**
- [ ] 배치 사이즈(20) 적절성 확인
- [ ] 검증 스크립트(Mock 위주) 방향성 동의

---

## 🎯 Core Strategy

### 1. Batch Processing 구현
`itertools.batched` (Python 3.12+) 또는 슬라이싱을 사용하여 `save_chunks` 메서드 내에서 루프를 돕니다.
```python
# Pseudo Code
batch_size = config.CHROMA_BATCH_SIZE
for i in range(0, len(chunks), batch_size):
    batch = chunks[i : i + batch_size]
    collection.add(...)
```

### 2. Configuration 관리
하드코딩을 피하고 `admin/config.py`의 `AdminConfig` 클래스에 설정을 추가하여 유연성을 확보합니다.

---

## 📂 Proposed Changes

### Configuration Layer

#### [MODIFY] `admin/config.py`
- `AdminConfig` 클래스에 `CHROMA_BATCH_SIZE: int = 20` 필드 추가.

---

### Infrastructure Layer

#### [MODIFY] `app/infrastructure/storage/chroma.py`
- `ChromaStorage.save_chunks` 메서드 리팩토링:
  - `chunks` 리스트를 배치 단위로 분할.
  - 각 배치마다 `self.collection.add` 호출.
  - 진행 상황 로깅 (`logger.info`).
  - 예외 발생 시 어떤 배치에서 실패했는지 로그에 기록.

---

## 🧪 Verification Plan

### Automated Tests

#### Unit Tests (New Script)
- **Script**: `scripts/test_robust_ingestion.py`
- **Method**: 
  - 50개의 더미 Chunk 생성.
  - `AdminConfig.CHROMA_BATCH_SIZE`를 20으로 설정(Mock).
  - `ChromaStorage`의 `collection.add` 메서드를 Mocking (`unittest.mock.MagicMock`).
  - `save_chunks` 호출 후 `collection.add`가 정확히 3번 호출되었는지 검증 (20, 20, 10).
  - 각 호출 시 전달된 ID가 올바른지 검증.

```bash
uv run python scripts/test_robust_ingestion.py
```

### Manual Verification
- **Scenario**: 실제 대형 문서 수집 (Optional)
    - `scripts/ingest_url.py` (또는 유사 스크립트)를 사용하여 `https://ko.wikipedia.org/wiki/일론_머스크` 수집 시도.
    - `verify_chroma_storage.py`로 총 청크 개수가 Neo4j와 일치하는지 확인.

---

## 📊 Expected Impact

### Stability
- 대형 문서 수집 성공률 100% 달성 (Data Drift 해소).

### Performance
- API 호출 횟수는 증가하지만(1회 -> N회), 각 호출의 Latency는 감소하고 Timeout 가능성은 현저히 낮아짐.
