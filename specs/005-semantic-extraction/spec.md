# Spec 005: Basic Semantic Extraction

## 1. 개요 (Overview)
본 Spec은 **"지능형 데이터로의 첫 걸음"**입니다. 단순히 Markdown 텍스트를 저장하는 것을 넘어, **Google Gemini Pro**를 활용하여 데이터에 "의미(Semantics)"를 부여하고 구조화합니다. 
이 과정은 향후 고도화된 지식 그래프(Knowledge Graph)로 나아가기 위한 필수적인 **재료 준비(Pre-processing)** 단계입니다.

## 2. 목표 (Goals)
- **정보의 구조화 (Structuring)**: 비정형 텍스트에서 정형화된 메타데이터(JSON)를 추출합니다.
- **점진적 진화의 기록 (Documenting Evolution)**: 왜 처음부터 거창한 그래프가 아닌 "단순 추출"부터 시작하는지, 그리고 이 데이터가 나중에 어떻게 활용되는지 그 **진화의 과정 자체를 문서화**하여 아키텍처 결정의 맥락을 남깁니다.

## 3. 상세 요구사항 (Requirements)

### 3.1 LLM 통합 및 라이브러리 선정 (Library & Integration)
- **`LangChain` (LCEL) 도입 이유**:
  - 현재는 단일 단계(Single-step)이지만, 표준화된 입출력 관리를 위해 채택했습니다.
- **모델**: Google `Gemini Pro` (Only).
  - *Decision*: 비용 효율성과 긴 컨텍스트 처리에 강점이 있는 Gemini를 단일 모델로 선정하여 초기 복잡도를 줄입니다.

### 3.2 추출 항목 및 선정 사유 (`ExtractedMetadata`)
단순히 "좋아 보여서" 뽑는 것이 아니라, **Spec 006/007(Graph/Ontology)**에서 노드로 변환될 잠재력을 가진 항목들입니다.

1.  **title** (Optional):
    *   *Why*: 크롤링된 HTML의 `<title>`은 불명확한 경우가 많습니다(예: "Home - Blog"). 내용 기반으로 정제된 제목을 확보하여 검색 품질을 높입니다.
2.  **summary**:
    *   *Why*: RAG(검색 증강) 시, 전체 문서를 읽지 않고 요약본만으로 관련성을 판단(Re-ranking)하거나, LLM Context에 요약만 주입하여 토큰을 절약하기 위함입니다.
3.  **keywords**:
    *   *Why*: 벡터 검색(유사도)의 한계를 보완하는 키워드 필터링(Exact Match) 용도입니다.
4.  **entities** (Person, Organization, Technology, Topic):
    *   *Why*: 이들은 향후 그래프 데이터베이스의 **Main Node**가 됩니다.
    *   지금 미리 분류해두지 않으면, 나중에 "Elon Musk"가 사람인지 회사인지 알 수 없어 그래프 연결(Relation)이 불가능해집니다.

### 3.3 설계 의도와 점진적 개선 (Design Rationale & Evolution)
- **왜 지금 `LangGraph`가 아닌가?**: 현재 로직은 `Input -> LLM -> JSON`의 직선형 구조입니다. 루프나 분기가 없는 상태에서 그래프 도구를 도입하는 것은 과도한 엔지니어링(Over-engineering)입니다.
- **미래와의 연결**: 지금 저장되는 `metadata.semantic_data`는 차후 마이그레이션 스크립트를 통해 Neo4j의 `(:Person)`, `(:Organization)` 노드로 승격될 것입니다. 이 Spec은 그 **데이터적 기반**을 닦는 작업입니다.

## 4. 아키텍처 (Architecture)
- **Service Layer**: `SemanticExtractor` 클래스를 통해 LLM 호출 캡슐화.
- **Pipeline**: `IngestionService` -> (Web Crawl) -> (Markdown Conversion) -> **(Semantic Extraction)** -> (Save DB).

## 5. 성공 기준 (Acceptance Criteria)
- `POST /ingest/web` 요청 시, 저장은 비동기로 이루어지며 작업 완료 후 DB 조회 시 `metadata.semantic_data` 필드에 요약 및 키워드가 존재해야 함.
- LLM 호출 실패 시에도 원본 문서는 저장되어야 함 (Partial Success 허용, 에러 로깅).
