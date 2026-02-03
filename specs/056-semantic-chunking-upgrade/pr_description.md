# feat(spec-056): semantic chunking upgrade

## 📋 Summary

### 배경 및 목적
RAG 시스템의 검색 품질을 높이기 위해 단순 고정 크기 분할(Recursive) 방식을 넘어, 문장의 의미적 흐름을 감지하여 분할하는 **Semantic Chunking** 기능을 도입했습니다. 이를 통해 검색 결과의 문맥 보존 능력을 극대화하고자 합니다.

### 주요 변경 사항
- [x] **Semantic Chunker 구현**: LangChain `Experimental` 패키지와 Gemini Embeddings를 활용한 의미 기반 분할 로직 추가.
- [x] **Chunker Factory 도입**: 요청별로 `recursive` 또는 `semantic` 전략을 동적으로 선택할 수 있는 구조 설계.
- [x] **Ingestion API 확장**: 청킹 설정을 API 요청 파라미터(`chunking_config`)로 전달할 수 있도록 확장.
- [x] **Admin UI 개선**: `Ingestion Management` 페이지에 전략 선택 및 임계값 설정 위젯 추가.
- [x] **영구 문서화**: `docs/features/semantic_chunking.md`에 아키텍처 및 확장 가이드 기록.

## 🎯 Key Review Points
1. **Infrastructure**: `LangChainSemanticChunker`가 Gemini 임베딩을 통해 브레이크포인트를 올바르게 감지하는지.
2. **Factory Design**: 기존 수집 프로세스의 하위 호환성을 해치지 않으면서 전략을 전환할 수 있는지.
3. **Embedding Extensibility**: 현재 Gemini 기반이나 OpenAI 등으로 교체가 용이하도록 추상화되어 있는지.

## 🧪 Verification

### Automated Tests
```bash
# Unit Test
uv run pytest tests/unit/infrastructure/chunker/test_semantic_chunker.py

# Integration Test
uv run pytest tests/integration/functional/test_ingestion_with_semantic.py
```

### Database Verification (Direct Query)
제공된 검증용 스크립트를 통해 DB 데이터를 직접 확인할 수 있습니다.
- `scripts/check_chroma_data.py`: ChromaDB 벡터 데이터 및 메타데이터 조회
- `scripts/verify_semantic_data.py`: Neo4j 작업 상태와 ChromaDB 연계 검증

## 📦 Files Changed

### 🆕 New Files
- `app/domain/value_objects/chunk_config.py`: 청킹 설정 VO
- `app/infrastructure/chunker/semantic_chunker.py`: 의미 기반 청커 구현체
- `app/infrastructure/chunker/chunker_factory.py`: 청커 생성 팩토리
- `docs/features/semantic_chunking.md`: 영구 기능 문서
- `scripts/check_chroma_data.py`, `scripts/verify_semantic_data.py`: 검증 도구
- `tests/unit/infrastructure/chunker/test_semantic_chunker.py`: 유닛 테스트
- `tests/integration/functional/test_ingestion_with_semantic.py`: 통합 테스트

### 🛠 Modified Files
- `app/application/services/ingestion.py`: 서비스 로직 연동
- `admin/pages/0_Ingestion_Management.py`: UI 위젯 추가
- `pyproject.toml`: 의존성(`langchain-experimental`) 추가

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `docs/features/semantic_chunking.md` 영구 문서화 완료
- [x] `walkthrough.md` 및 `pr_description.md` 작성 완료
- [x] 검증용 도구(scripts) 포함 및 커밋 완료
