# Implementation Plan - Spec 005: Basic Semantic Extraction

## 목표 (Goal)
**Google Gemini Pro**를 활용하여 인제스션 파이프라인에 시맨틱 추출 단계를 구현하고, 시스템의 "**지능형 데이터로의 첫 걸음(Seed of Intelligence)**"을 확립합니다. 이 과정은 구조화된 메타데이터(요약, 키워드, 엔티티)를 추출하는 것뿐만 아니라, 단순 추출에서 향후 지식 그래프로 발전해 나가는 **아키텍처의 진화 과정을 문서화**하는 것을 포함합니다.

## 승인 요청 (User Review Required)
> [!IMPORTANT]
> **API Key 필요**: Gemini Pro를 사용하기 위해 `.env` 파일에 유효한 `GOOGLE_API_KEY`가 설정되어야 합니다.
> **의존성 추가**: 이번 변경으로 `langchain` 및 `langchain-google-genai` 라이브러리가 프로젝트에 추가됩니다.

## 변경 제안 (Proposed Changes)

### 설정 및 의존성 (Configuration & Dependencies)
#### [MODIFY] [pyproject.toml](file:///Users/ck/Project/doit/rag-ingestion/pyproject.toml)
- `langchain>=0.1.0` 추가
- `langchain-google-genai>=0.0.9` 추가

#### [MODIFY] [.env.example](file:///Users/ck/Project/doit/rag-ingestion/.env.example)
- `GOOGLE_API_KEY=` 템플릿 추가

### Core Layer
#### [NEW] [app/core/llm.py](file:///Users/ck/Project/doit/rag-ingestion/app/core/llm.py)
- `LLMFactory` 또는 `get_llm()` 함수 구현: `ChatGoogleGenerativeAI` 초기화.
- 클라이언트의 싱글톤 패턴 또는 효율적인 재사용 보장.

### Domain Layer
#### [NEW] [app/domain/schemas/extraction.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/extraction.py)
- `ExtractedMetadata` Pydantic 모델 정의:
    - `summary`: str (요약)
    - `keywords`: List[str] (키워드)
    - `entities`: Dict[str, List[str]] (Person, Org, Tech 등 엔티티 분류)

#### [NEW] [app/domain/services/semantic_extractor.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/services/semantic_extractor.py)
- `SemanticExtractor` 클래스 생성.
- LangChain `PromptTemplate` 및 `PydanticOutputParser`를 사용하여 안정적인 JSON 생성.
- `extract(text: str) -> ExtractedMetadata` 메서드 구현.

### Service Layer (Integration)
#### [MODIFY] [app/domain/services/ingestion.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/services/ingestion.py)
- `IngestionService`에 `SemanticExtractor` 주입.
- `process_job` 내에서: 원본 문서를 저장한 후(또는 트랜잭션 범위에 따라 그 전) `extractor.extract(content)` 호출.
- `AtomicDocument` 생성 시 추출된 메타데이터를 포함하도록 업데이트.

### Documentation (Design & Rationale)
#### [MODIFY] [specs/005-semantic-extraction/spec.md](file:///Users/ck/Project/doit/rag-ingestion/specs/005-semantic-extraction/spec.md)
- **설계 의도 기술**: 아키텍처가 단순 추출에서 지식 그래프로 진화하는 과정(Evolutionary Process)을 상세히 기술.
- **LCEL 선정 사유**: LangChain Expression Language(LCEL)를 사용하여 체인을 구성하는 이유(표준화, 가독성)와 향후 확장성 기술.
- **데이터 구조화의 목적**: 각 메타데이터 필드(Entities 등)가 온톨로지 관점에서 왜 필요한지 명시.

## 검증 계획 (Verification Plan)

### 자동화 테스트 (Automated Tests)
- **단위 테스트**: `tests/unit/domain/test_extractor.py`
    - `ChatGoogleGenerativeAI`를 Mocking하여 사전 정의된 JSON 문자열 반환.
    - `SemanticExtractor`가 응답을 `ExtractedMetadata`로 정확히 파싱하는지 검증.
    - 실행: `uv run pytest tests/unit/domain/test_extractor.py`

### 수동 검증 (Manual Verification)
1. **설정**: `.env`에 `GOOGLE_API_KEY` 추가.
2. **서버 실행**: `uv run uvicorn app.interfaces.api.main:app --reload`
3. **인제스션 요청**: `POST /ingest/web`으로 테스트 URL 전송 (예: 기술 블로그).
4. **결과 확인**:
    - `GET /documents/{doc_id}` (또는 Admin Dashboard)를 통해 `metadata` 필드에 `summary`, `keywords`, `entities`가 포함되어 있는지 확인.
