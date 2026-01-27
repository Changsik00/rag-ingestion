# Spec 043: Robust Ingestion (Chroma Batching)

## 📋 배경 및 문제 정의 (Background & Problem)

### 현재 상황
**Spec 044(이후 043으로 변경)** 관련하여 대형 문서 수집을 시도했으나, 데이터 정합성 문제가 발견되었습니다. 특히 '일론 머스크' 위키피디아 페이지와 같이 청크가 많은(약 159개) 문서를 수집할 때, Graph DB(Neo4j)에는 정상적으로 저장되지만 **Vector DB(ChromaDB)에는 단 한 건도 저장되지 않는 현상(Data Drift)**이 발생했습니다.

### 문제점
1. **API Timeout / Payload Limit**: `ChromaStorage.save_chunks`가 159개의 청크를 한 번의 `collection.add` 호출로 처리하려다 실패하는 것으로 추정됩니다.
2. **Data Consistency**: Neo4j는 성공하고 Chroma는 실패하여, "Graph에는 있지만 검색은 안 되는" 좀비 데이터가 생성됩니다.
3. **Retrieval Quality**: 하이브리드 검색 시 Vector 결과가 0건이 되어 검색 품질이 저하됩니다.

### 해결 방안
**ChromaDB 저장 로직에 배치(Batching) 처리**를 도입합니다.
- 한 번에 대량으로 저장하는 대신, 설정된 `BATCH_SIZE`(예: 20)만큼 나누어 순차적으로 저장합니다.
- 이를 통해 API 부하를 분산하고 저장 안정성을 확보합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **Batch Processing**: `ChromaStorage.save_chunks`는 입력된 청크 리스트를 `CHROMA_BATCH_SIZE` 단위로 나누어 처리해야 합니다.
2. **Configuration**: 배치 크기는 `AdminConfig`를 통해 제어 가능해야 합니다 (Default: 20).
3. **Logging**: 각 배치 저장 진행 상황(예: "Saving batch 1/8...")을 로그로 남겨야 합니다.

### Non-Functional Requirements
1. **Stability**: 159개 이상의 청크를 가진 문서도 Timeout 없이 저장되어야 합니다.
2. **Consistency**: 배치 처리 중 하나라도 실패하면(Partial Failure) 로그를 남기고 심각한 오류로 취급해야 합니다 (Transaction은 지원하지 않지만, 최대한 Atomic하게 동작하도록 유도).

## ✅ Definition of Done
1. `AdminConfig`에 `CHROMA_BATCH_SIZE` 설정 추가
2. `ChromaStorage` 리팩토링 및 Unit Test 작성 (Mocking을 통해 Batch 호출 횟수 검증)
3. 대형 문서(청크 50개 이상) 수집 시나리오 검증 스크립트(`scripts/test_robust_ingestion.py`) 통과
4. `scripts/repro_ingestion_failure.py` (실제 환경 재현) 성공 (Optional: 환경 허용 시)
