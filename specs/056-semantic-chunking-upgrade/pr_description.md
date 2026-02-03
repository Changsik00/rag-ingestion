# feat(chunking): implement semantic chunking upgrade

## 📋 Summary

### 배경 및 목적
프로젝트의 RAG 품질 고도화를 위해 기존의 고정 크기 분할(RecursiveCharacterTextSplitter) 방식을 의미 기반 분할(Semantic Chunking)로 확장합니다. 문맥의 의미적 연결성을 보존하여 검색 정확도를 높이는 것이 목표입니다.

### 주요 변경 사항
- [x] **Semantic Chunker 도입**: LangChain의 `SemanticChunker`와 Gemini Embeddings를 연동하여 의미적 브레이크포인트 감지 로직 구현.
- [x] **Chunker Factory 패턴 적용**: 요청에 따라 `recursive`와 `semantic` 전략을 동적으로 선택할 수 있는 구조 구축.
- [x] **Ingestion API 확장**: `IngestRequest` 및 `IngestionJob`에 청킹 설정을 추가하여 비동기 처리 시에도 설정값 유지.
- [x] **Admin UI 연동**: `Ingestion Management` 페이지에 전략 선택 및 임계값 튜닝을 위한 UI 위젯 추가.
- [x] **모니터링 강화**: `JobResponse`에 `docs_ids`를 추가하여 인입 결과를 명확히 확인할 수 있도록 개선.

## 🎯 Key Review Points
1. `ChunkerFactory`를 통한 다중 전략 처리 방식의 적절성.
2. `SemanticChunker` 도입으로 인한 의존성(`langchain-experimental`) 추가 및 성능 영향.
3. Admin UI에서의 설정값 주입 및 API 연동 로직.

## 🧪 Verification
- `tests/unit/infrastructure/chunker/test_semantic_chunker.py`: 의미상 다른 주제의 문장 분할 성공 확인.
- `tests/integration/functional/test_ingestion_with_semantic.py`: API-Service-Repo-DB에 이르는 전체 수집 Flow 검증 완료.

## 📦 Files Changed
(총 13개 파일 변경)
- `app/domain/value_objects/chunk_config.py`
- `app/infrastructure/chunker/semantic_chunker.py`
- `app/infrastructure/chunker/chunker_factory.py`
- `app/infrastructure/chunker/langchain_chunker.py`
- `app/application/services/ingestion.py`
- `app/domain/entities/job.py`
- `app/interfaces/api/v1/dto/ingest.py`
- `app/interfaces/api/v1/dto/jobs.py`
- `app/interfaces/api/v1/endpoints/ingest.py`
- `app/interfaces/api/v1/endpoints/jobs.py`
- `app/interfaces/api/dependencies.py`
- `admin/pages/0_Ingestion_Management.py`
- `pyproject.toml`
