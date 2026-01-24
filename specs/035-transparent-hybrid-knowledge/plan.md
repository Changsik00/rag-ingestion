# Implementation Plan: Spec-035

## 📋 Branch Strategy
- `feature/035-hybrid-knowledge`

## 🛑 User Review Required

1.  **Citation Notation**: `[1]`와 같은 숫자 인덱스 방식을 채택합니다.
2.  **LLM Knowledge Mark**: LLM의 자체 지식으로 답변한 문장에는 별도의 번호를 부여하지 않음으로써, **"번호가 있는 정보 = 검증된 DB 정보"**, **"번호가 없는 정보 = AI의 보충 지식"**으로 자연스럽게 구분하게 합니다. (추가로 답변 하단에 "일부 정보는 AI의 배경 지식을 바탕으로 작성되었습니다"라는 문구를 삽입할 수 있습니다.)

## 🎯 Core Strategy

### 1. "Sparse but Strong" Prompting
RAG 데이터가 한 줄뿐이더라도 답변에 포함시키고 `[1]`을 달게 합니다. LLM에게는 다음과 같이 지시합니다:
- "제공된 Context(DB)는 절대적인 팩트입니다. 이를 우선적으로 사용하고 인라인 인덱스를 다세요."
- "DB에 없는 내용은 당신의 지식으로 보강하되, 인라인 인덱스를 달지 마세요."
- "이 두 정보를 자연스러운 한 문단으로 융합하세요."

### 2. Post-Processing & Parsing
LLM이 생성한 텍스트에서 정규표현식(`\[(\d+)\]`)을 사용하여 사용된 모든 인덱스를 추출합니다. 이 인덱스를 바탕으로 `RAGGraphState`에 저장된 원본 `Chunk` 데이터(제목, URL 등)와 매칭하여 최종 `citations` 리스트를 구성합니다.

### 3. Graceful Fallback (Hybrid)
기존에는 컨텍스트가 없으면 답변을 거부했지만, 이제는 "제시된 컨텍스트에는 관련 정보가 없으나, 일반적인 지식을 바탕으로 답변해 드리겠습니다"라는 가이드와 함께 LLM의 지식을 출력하도록 `generate_answer` 노드의 로직을 수정합니다.

## 📂 Proposed Changes

### [Documentation & Strategy]

#### [NEW] `docs/design_guides/006-hybrid-knowledge-mixing.md`
- **Sparse but Powerful** 전략 상세 기술.
- RAG 데이터와 LLM 지식의 융합 원칙, Citation 부여 기준, 그리고 이러한 설계가 도출된 배경(User-Agent 대화 맥락) 정리.

### [RAG Domain]

#### [MODIFY] `app/domain/rag/state.py`
- `citations: list[dict]` 추가: `[{"index": 1, "title": "...", "url": "..."}]`

### [Infrastructure & Nodes]

#### [MODIFY] `app/infrastructure/rag/nodes.py`
- `_prepare_context_with_indices()`: 컨텍스트 문자열 생성 시 청크별 인덱스(`[ID: n]`) 부여 로직 추가.
- `generate_answer()`:
    - **System Prompt**: 하이브리드 지식 활용 가이드라인 + Citation 규칙 주입.
    - **Output Parsing**: 정규식을 통해 사용된 인덱스 추출 → State의 `citations` 필드 업데이트.

### [Admin Dashboard]

#### [MODIFY] `app/admin/pages/4_RAG_Playground.py`
- `render_debug_ui()` 수정: `citations` 정보를 읽어와 답변 하단에 "참조 문헌" 리스트 자동 생성.
- Citation 번호를 클릭하면 원본 소스 페이지가 새 탭에서 열리도록 마크다운 링크 구성.

## 🧪 Verification Plan (TDD/BDD)

### BDD Scenarios (Integration)
`tests/integration/bdd/test_hybrid_knowledge.py` 파일에 다음 시나리오 구현:
1. **Hybrid Retrieval Flow**: 특정 문서 필터링에도 불구하고 부족한 정보는 LLM 지식으로 채우는지 검증.
2. **Citation Consistency**: 생성된 답변의 `[n]` 번호의 개수가 `state["citations"]` 리스트의 길이와 일치하는지 검증.

### Unit Testing (TDD)
1. **`test_extract_citations_from_text`**: 정규식을 통한 인덱스 추출 기능 선구현 후 개발.
2. **`test_context_serialization_with_ids`**: 컨텍스트 청크에 ID가 올바르게 주입되는지 검증.

### Manual Verification
1. Playground에서 "일론 머스크와 스티브 잡스 비교" (테스트 데이터 수집 후)
2. 답변의 인라인 인덱스(`[1]`)와 하단 Reference 리스트의 일치 여부 확인.
3. Reference 링크 클릭 시 원본 URL 이동 확인.
