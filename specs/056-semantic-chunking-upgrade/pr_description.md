# feat(spec-056): semantic chunking upgrade

## 📋 Summary

### 배경 및 목적
RAG 시스템의 검색 품질을 높이기 위해 단순 고정 크기 분할(Recursive) 방식을 넘어, 문장의 의미적 흐름을 감지하여 분할하는 **Semantic Chunking** 기능을 도입했습니다. 이를 통해 검색 결과의 문맥 보존 능력을 극대화하고자 합니다.

### 주요 변경 사항
- [x] **Semantic Chunker 구현**: LangChain `Experimental` 패캐지와 Gemini Embeddings를 활용한 의미 기반 분할 로직 추가.
- [x] **Chunker Factory 도입**: 요청별로 `recursive` 또는 `semantic` 전략을 동적으로 선택할 수 있는 구조 설계.
- [x] **Ingestion API 확장**: 청킹 설정을 API 요청 파라미터(`chunking_config`)로 전달할 수 있도록 확장.
- [x] **Admin UI 개선**: `Ingestion Management` 페이지에 전략 선택 및 임계값 설정 위젯 추가.

## 🎯 Key Review Points
1. **Infrastructure**: `LangChainSemanticChunker`가 Gemini 임베딩을 통해 브레이크포인트를 올바르게 감지하는지.
2. **Factory Design**: 기존 수집 프로세스의 하위 호환성을 해치지 않으면서 전략을 전환할 수 있는지.
3. **UI/UX**: 사용자 친화적인 설정 위젯 배치 및 파라미터 전달 로직.

## 🧪 Verification

### Automated Tests
```bash
# Unit Test
uv run pytest tests/unit/infrastructure/chunker/test_semantic_chunker.py

# Integration Test
uv run pytest tests/integration/functional/test_ingestion_with_semantic.py
```
**테스트 결과 요약:**
- ✅ `test_semantic_chunker_splitting`: 서로 다른 주제의 문장을 구분하여 청킹 완료.
- ✅ `test_ingestion_with_semantic_chunking`: API 호출 시 주입된 설정에 따라 실제 DB에 청크가 생성됨을 확인.

### Database Verification (Direct Query)
수집된 데이터에 `semantic` 전략이 적용되었는지 직접 DB에서 확인할 수 있습니다.

**ChromaDB (Vector DB):**
```python
# Semantic 전략으로 생성된 청크 조회
res = repo.collection.get(where={'chunking_strategy': 'semantic'}, limit=2)
```

**Neo4j (Graph DB):**
```cypher
MATCH (j:IngestionJob)
WHERE j.status = 'COMPLETED'
RETURN j.job_id, j.source_url, j.chunking_config
ORDER BY j.created_at DESC LIMIT 5
```

## 📦 Files Changed

### 🆕 New Files
- `app/domain/value_objects/chunk_config.py`: 청킹 설정 VO
- `app/infrastructure/chunker/semantic_chunker.py`: 의미 기반 청커 구현체
- `app/infrastructure/chunker/chunker_factory.py`: 청커 생성 팩토리
- `specs/056-semantic-chunking-upgrade/spec.md`: 기능 명세서
- `specs/056-semantic-chunking-upgrade/plan.md`: 구현 계획서
- `specs/056-semantic-chunking-upgrade/task.md`: 작업 현황판
- `tests/unit/infrastructure/chunker/test_semantic_chunker.py`: 유닛 테스트
- `tests/integration/functional/test_ingestion_with_semantic.py`: 통합 테스트

### 🛠 Modified Files
- `app/application/services/ingestion.py`: 서비스 로직 연동
- `admin/pages/0_Ingestion_Management.py`: UI 위젯 추가
- `pyproject.toml`: 의존성(`langchain-experimental`) 추가

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
