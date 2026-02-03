# Spec 056: Semantic Chunking Upgrade

## 📋 Summary

### 배경 및 목적
현재 시스템은 `RecursiveCharacterTextSplitter`를 사용하여 문자를 기준으로 재귀적으로 분할합니다. 이는 빠르지만 문맥의 의미적 경계를 무너뜨릴 수 있으며, 특히 복잡한 논리나 설명이 포함된 문서에서 RAG 검색 품질을 저하시키는 원인이 됩니다.
본 스펙은 **의미적 유사성(Semantic Similarity)**을 기반으로 문장을 그룹화하여 청크를 생성하는 **Semantic Chunking** 기능을 도입하여 검색의 밀도와 정확도를 높이는 것을 목적으로 합니다.

### 주요 목표
1.  **의미 기반 분할**: 문장 간 임베딩 유사도를 계산하여 의미가 변하는 지점(Breakpoint)에서 분할.
2.  **유연한 설정**: 유사도 임계치(Threshold) 및 통계적 방법(Percentile, Standard Deviation 등)을 사용자 설정 가능하게 구현.
3.  **기존 구조 유지**: `Chunker` 인터페이스를 확장하여 기존의 `Recursive` 방식과 선택적으로 사용할 수 있도록 설계.
4.  **Admin UI 연동**: Ingestion 시 청킹 전략을 선택하고 상세 파라미터를 조절할 수 있는 UI 제공.

## 🛠 Proposed Changes

### 1. Domain Layer (`app/domain`)
- **`app/domain/interfaces/chunker.py`**: 인터페이스는 유지하되, 필요시 설정을 주입받을 수 있는 구조 검토.
- **`app/domain/value_objects/chunk_config.py` [NEW]**: 청킹 전략(Recursive, Semantic) 및 관련 파라미터(chunk_size, threshold_type 등)를 담는 Value Object 정의.

### 2. Infrastructure Layer (`app/infrastructure`)
- **`app/infrastructure/chunker/semantic_chunker.py` [NEW]**: LangChain의 `SemanticChunker`를 래핑하여 구현.
    - OpenAI 또는 Local 임베딩 모델 사용.
    - `percentile`, `standard_deviation`, `interquartile` 등 다양한 브레이크포인트 감지 로직 지원.
- **`app/infrastructure/chunker/chunker_factory.py` [NEW]**: 전략에 따라 적절한 `Chunker` 인스턴스를 생성하는 팩토리 클래스.

### 3. Application Layer (`app/application`)
- **`app/application/services/ingestion.py`**: `IngestionService`가 `ChunkerFactory`를 사용하여 사용자가 요청한 전략으로 문서를 분할하도록 수정.

### 4. Interface Layer (`app/interfaces`)
- **`app/interfaces/api/v1/dto/ingest.py`**: `IngestRequest` DTO에 `chunking_config` 필드 추가.
- **`admin/pages/4_RAG_Playground.py` (또는 신규 Ingestion 페이지)**: 청킹 전략 선택 위젯 추가.

## 🧪 Verification Plan

### Automated Tests
- **Unit Test**: `SemanticChunker`가 동일한 의미의 문장을 하나의 청크로 묶는지 테스트.
- **Integration Test**: API를 통해 임계치를 변경하며 Ingestion을 수행하고, 생성된 청크의 개수와 품질 확인.

### Manual Verification
- Streamlit Admin UI에서 "Semantic" 모드를 선택하고 샘플 문서를 업로드하여 기존 "Recursive" 방식과 청크 분할 결과 비교.

## ⚠️ Consideration
- **임베딩 모델 확장성**: 현재는 비용 효율성을 위해 Google(Gemini) 임베딩을 기본으로 사용하지만, `langchain-experimental` 인터페이스를 사용하므로 OpenAI 등 타 모델로의 교체가 매우 용이하도록 설계되었습니다. 향후 필요에 따라 런타임에 모델을 선택할 수 있는 기능을 추가할 수 있습니다.
- **비용/속도**: Semantic Chunking은 각 문장마다 임베딩을 생성하므로 API 비용과 처리 시간이 증가합니다. 이를 위해 기본값 최적화 및 사용자 경고 UI가 필요할 수 있습니다.
- **의존성**: `langchain-experimental` 패키지가 필요할 수 있으므로 `pyproject.toml` 업데이트가 필요합니다.
