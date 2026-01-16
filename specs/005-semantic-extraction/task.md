# Task Checklist - Spec 005: Basic Semantic Extraction

## 0. 문서화 및 설계 의도 (Documentation & Design)
- [x] **설계 의도 기술**: `spec.md`에 라이브러리 선정 이유(LangChain)와 점진적 개선(Ontology) 전략 명시
- [x] **백로그 점검**: Spec 005 결과물이 향후 Spec 006/007(Graph)과 어떻게 연결되는지 `queue.md` 및 `spec.md`에 반영

## 1. 환경 및 설정 (Environment Setup)
- [x] **의존성 추가**
    - [x] `langchain`, `langchain-google-genai` 라이브러리 추가 (`pyproject.toml`)
    - [x] `.env` 파일에 API Key 설정 (`GOOGLE_API_KEY`) template 추가

## 2. Core & Domain Layer (핵심 로직)
- [x] **LLM 클라이언트 설정**
    - [x] `app/core/llm.py`: Singleton 또는 Factory 패턴으로 LLM 클라이언트 초기화 로직 구현
- [x] **프롬프트 및 파서 설계**
    - [x] `app/domain/prompts/substruction.py`: 엔티티 추출을 위한 프롬프트 템플릿 작성 (Implemented inline in `SemanticExtractor`)
    - [x] `app/domain/schemas/extraction.py`: Pydantic 기반 추출 스키마 정의 (`ExtractedMetadata`)
- [x] **추출 서비스 구현**
    - [x] `app/domain/services/semantic_extractor.py`: 텍스트 -> 메타데이터 변환 로직 구현

## 3. Integration (파이프라인 연동)
- [x] **Ingestion Service 연동**
    - [x] `IngestionService.process_job` 흐름에 `SemanticeExtractor` 단계 추가
    - [x] 추출된 메타데이터를 Document와 함께 저장 (DB 스키마 변경 필요 시 반영)

## 4. 검증 (Verification)
- [x] **단위 테스트**
    - [x] LLM 응답 Mocking 하여 추출 로직 테스트 (`tests/domain/test_extractor.py`)
- [x] **통합 테스트**
    - [x] 실제 웹 수집 후 메타데이터가 정상적으로 추출/저장되는지 확인
