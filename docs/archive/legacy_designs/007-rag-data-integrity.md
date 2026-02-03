# Design Guide 007: RAG Quality Stabilization & Data Integrity

## 1. 배경 (Background)
RAG 시스템의 성능은 검색된 데이터의 품질(Quality)과 정합성(Integrity)에 직결됩니다. 현재 시스템에서 발견된 주요 병목 현상은 다음과 같습니다:
- **Index Drift**: Vector DB(ChromaDB)와 Graph DB(Neo4j) 간의 인덱싱 누락으로 인한 검색 불일치.
- **Metadata Sparsity**: 문서의 제목(Title)이 없어 검색 결과의 가독성 및 필터링 성능 저하.
- **Context Noise**: 불필요한 마크다운 요소(네비게이션 박스, 무의미한 표 등)가 LLM의 추론 성능을 방해.

## 2. 데이터 정합성 강화 (Data Integrity Sync)
Vector DB와 Graph DB 간의 상태를 동기화하기 위한 전략입니다.

### 2.1 동기화 메커니즘
- **Missing Link Detection**: Neo4j에 존재하지만 ChromaDB에 임베딩되지 않은 `Chunk` ID 리스트를 추출합니다.
- **Incremental Re-indexing**: 누락된 데이터에 대해서만 Gemini Embedding API를 사용하여 재인덱싱을 수행합니다.
- **Retry Strategy**: 임베딩 생성 시 발생하는 Rate Limit(429 Error)에 대해 Exponential Backoff 기반의 재시도 로직을 적용합니다.

## 3. 메타데이터 풍부화 (Metadata Enrichment)
문서 수집 시 최소한의 식별 정보를 보장합니다.

### 3.1 제목 추출 전략 (Title Fallback)
1. **Scraper Metadata**: 스크래퍼가 추출한 메타데이터를 우선 사용.
2. **URL Based Extraction**: 제목이 없을 경우 URL의 마지막 경로를 정규화하여 사용.
3. **Content Extraction**: URL이 모호할 경우 본문의 첫 번째 <h1> 태그 또는 첫 문장을 제목으로 대체.

## 4. 컨텍스트 정제 (Context Cleaning)
LLM에게 전달되기 전 브레인 레이어에서 수행하는 데이터 가공 단계입니다.

### 4.1 노이즈 제거 대상
- 위키피디아의 `navbox`, `sidebar` 등 구조적 마크다운 요소.
- 텍스트가 없는 연속적인 마크다운 표 (`| | |`).
- 이미지 경로 및 무의미한 아이콘 링크.

## 5. 실행 및 관리 (Execution)
- **Sync Tool**: `scripts/sync_indices.py`를 통해 수동 또는 스케줄링된 동기화 지원.
- **Logging**: 인제스션 과정에서 각 저장소별 저장 성공 여부를 독립적으로 로깅하여 추적성 확보.
