# Feature: Semantic Chunking

## 📋 개요
Semantic Chunking은 문서를 단순히 일정한 글자 수나 행 단위로 나누는 대신, 문장 간의 **의미적 유사성(Semantic Similarity)**을 분석하여 주제가 바뀌는 지점에서 지능적으로 분할하는 기능입니다. 이를 통해 RAG 검색 시 문맥의 품질을 극대화합니다.

## 🛠 아키텍처 및 전략

### 1. 분할 로직 (Chunking Strategy)
- **임베딩 기반 유사도 계산**: 각 문장을 임베딩 벡터로 변환하고, 인접한 문장 간의 코사인 유사도를 계산합니다.
- **브레이크포인트 감지**: 유사도가 급격히 떨어지는(거리가 멀어지는) 지점을 분할 지점으로 결정합니다.
- **지원 알고리즘**:
    - `percentile` (기본값: 90.0): 유사도 분포의 상위 백분위수를 기준으로 분할.
    - `standard_deviation`: 표준 편차 기반 분할.
    - `interquartile`: 사분위 범위 기반 분할.

### 2. 임베딩 모델 확장성
현재 시스템은 런타임 성능과 비용을 고려하여 **Google Gemini (embedding-001)** 모델을 기본으로 사용합니다. 하지만 아키텍처는 모델 불가지론적(Model-agnostic)으로 설계되어 있어 다음과 같은 확장이 용이합니다.
- **OpenAI**: `text-embedding-3-small/large` 모델로 교체 가능.
- **Local 모델**: HuggingFace의 `BGE`, `KoSimCSE` 등 로컬 임베딩 모델 연동 가능.

## 📥 사용 방법

### API 호출
수집 요청 시 `chunking_config` 필드를 통해 전략을 지정할 수 있습니다.
```json
{
  "url": "...",
  "chunking_config": {
    "strategy": "semantic",
    "breakpoint_threshold_type": "percentile",
    "breakpoint_threshold_amount": 90.0
  }
}
```

### Admin UI
- `Ingestion Management` 페이지의 **Chunking Settings** 섹션에서 시각적으로 설정할 수 있습니다.

## 🧪 검증 및 디버깅

### 데이터 검증 (Direct Query)
청크 메타데이터의 `chunking_strategy` 필드를 확인하여 적용 여부를 판단합니다.

**ChromaDB:**
```python
# Semantic 전략 청크 조회 예시
res = collection.get(where={'chunking_strategy': 'semantic'}, limit=5)
```

**Neo4j:**
```cypher
MATCH (j:IngestionJob)
RETURN j.job_id, j.chunking_config
ORDER BY j.created_at DESC LIMIT 5
```

## ⚠️ 고려 사항
- **비용**: 모든 문장에 대해 임베딩을 생성하므로 단순 분할 방식보다 API 비용이 발생합니다.
- **속도**: 임베딩 생성 및 유사도 계산을 위한 추가 지연 시간이 발생할 수 있습니다.
