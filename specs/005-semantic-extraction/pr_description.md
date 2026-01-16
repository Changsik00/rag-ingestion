# 🧠 Spec 005: Basic Semantic Extraction

## 📋 Summary

**"지능의 씨앗(Seed of Intelligence)"** 구현 완료

Google Gemini 2.0를 활용하여 수집된 문서에서 구조화된 메타데이터를 자동 추출하는 기능을 구현했습니다. 이는 향후 Knowledge Graph 구축(Spec 006/007)을 위한 핵심 기반입니다.

**주요 구현**:
- 🏗️ **Core Layer**: LLM Factory 패턴으로 Gemini 클라이언트 관리
- 🎯 **Domain Layer**: SemanticExtractor 서비스 및 구조화된 메타데이터 스키마
- 🔗 **Integration**: IngestionService에 자동 추출 로직 통합
- ✅ **Tests**: 단위 테스트 작성 및 통과 (2 passed)

**기술 스택 현대화**:
- Python 3.9 → 3.12
- LangChain 0.1 → 0.3+
- langchain-google-genai 0.0.9 → 4.1+
- Gemini Model: `gemini-2.0-flash-exp` 적용

---

## 🔍 Key Review Points

### 1. 라이브러리 업그레이드 결정
- **문제**: 초기 구현 중 Gemini API 404 오류 발생 (legacy `v1beta` API 사용)
- **해결**: `langchain-google-genai>=4.0.0`으로 업그레이드하여 최신 `google-genai` SDK 사용
- **영향**: Python 3.10+ 요구사항으로 인한 `.python-version` 변경 (3.9 → 3.12)
- **검토 포인트**: 프로덕션 환경의 Python 버전 호환성 확인 필요

### 2. LangChain 0.3 호환성
- **변경 사항**: `langchain.prompts` → `langchain_core.prompts`
- **파일**: [`app/domain/services/semantic_extractor.py`](file:///Users/ck/Project/doit/rag-ingestion/app/domain/services/semantic_extractor.py#L3-L4)
- **검토 포인트**: 다른 LangChain 사용 코드와의 충돌 여부 확인

### 3. 추출 메타데이터 구조
```python
class ExtractedMetadata(BaseModel):
    title: Optional[str]
    summary: str
    keywords: List[str]
    entities: Dict[str, List[str]]
```
- **검토 포인트**: 향후 Ontology 설계 시 충분한 정보를 제공하는지 검토

### 4. LangChain vs LangGraph 전략
- **현재**: LCEL(LangChain Expression Language) 사용
- **향후**: Phase 4에서 LangGraph 마이그레이션 계획됨
- **검토 포인트**: 현재 단순 파이프라인으로 충분한지 확인

---

## ✅ Verification Plan

### Automated Tests

```bash
# 단위 테스트 실행
uv run pytest tests/unit/domain/test_extractor.py

# 전체 테스트 실행
uv run pytest
```

**예상 결과**: ✅ `2 passed` (SemanticExtractor 성공/실패 시나리오)

### Manual Verification

> [!WARNING]
> **통합 테스트 미완료**: 실제 Gemini API 호출 검증이 필요합니다.

#### 1. 환경 설정

```bash
# .env 파일에 API Key 추가
echo "GOOGLE_API_KEY=YOUR_API_KEY" >> .env
```

#### 2. 독립 스크립트 테스트

```bash
uv run python scripts/manual_verify_extraction.py
```

**예상 출력**:
```
🔑 API Key found: AIzaS...
🚀 Sending text to SemanticExtractor (Gemini)...
✅ Extraction Successful!
Title: ...
Summary: ...
Keywords: [...]
Entities: {...}
```

#### 3. 실제 파이프라인 테스트

```bash
# API 서버 실행
uv run uvicorn app.interfaces.api.main:app --reload

# 웹 수집 요청
curl -X POST "http://localhost:8000/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'

# 응답에서 job_id 확인 후
curl "http://localhost:8000/jobs/{job_id}"
```

**검증 항목**:
- [ ] Job Status가 `COMPLETED`로 변경되는지
- [ ] Document의 `metadata` 필드에 추출 결과가 포함되는지
- [ ] Neo4j/ChromaDB에 메타데이터가 저장되는지

#### 4. 메타데이터 품질 검증

추출된 메타데이터가 다음 기준을 만족하는지 확인:
- **Title**: 문서 내용을 정확히 반영
- **Summary**: 핵심 내용을 3문장으로 요약
- **Keywords**: 5-10개의 관련성 높은 키워드
- **Entities**: 타입별 분류가 적절한지 (Person, Organization, Technology 등)

---

## 🛠️ Tech Stack

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `langchain` | `>=0.3.0` | LCEL 파이프라인 구성 |
| `langchain-google-genai` | `>=4.0.0` | Gemini 2.0 통합 |
| `pydantic` | `>=2.12.5` | 구조화된 출력 스키마 |

### Model

- **Provider**: Google Gemini
- **Model**: `gemini-2.0-flash-exp`
- **Reason**: 무료 티어, 빠른 응답, Structured Output 지원

### Python Version

- **Before**: 3.9.6
- **After**: 3.12
- **Reason**: `langchain-google-genai>=4.0.0` 요구사항

---

## 📦 Commit History

```
7953b16 feat: update default model to gemini-2.0-flash-exp
7487deb refactor: update imports to langchain_core for 0.3 compatibility
f5b6a6d chore: upgrade to python 3.12 and langchain 0.3+ stack
00297ed docs: update task checklist for spec-005 implementation
72139fe feat(usecase): integrate semantic extractor into ingestion pipeline
ff7e828 feat(domain): implement semantic extractor service and schema
46795b0 feat(core): implement LLM client factory
214bfa8 chore: add dependencies and env config for spec-005
c1a97c8 docs: update backlog and specs for spec-005
```

---

## 🚀 Next Steps

1. ✅ **PR Merge** (사용자 통합 테스트 후)
2. 📊 **Spec 006: Ontology Design** - 추출된 엔티티를 그래프 노드로 매핑
3. 🕸️ **Spec 007: Knowledge Graph Construction** - Neo4j에 관계 구축
