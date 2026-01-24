# Spec-035: Transparent Hybrid Knowledge Strategy (RAG Resilience)

## 📋 배경 및 문제 정의 (Background & Problem)

현재의 "Strict RAG" 시스템은 DB에 있는 정보만을 진실로 간주하며, Context에 데이터가 없으면 답변을 거부합니다. 이는 데이터 중심 서비스에서는 신뢰의 핵심이지만, 실제 사용 환경에서는 다음과 같은 **"정보의 단절"** 문제를 야기합니다.

1.  **필터 이름 불일치 (Semantic Gap)**: "엔비디아와 삼성 비교" 질문 시, DB에 'Nvidia'와 'Samsung Electronics'라는 이름으로 저장되어 있다면, 현재의 Intent Classifier는 한국어-영어 매핑의 미세한 차이로 인해 필터를 걸고, 검색 결과가 0건이 되어 "모른다"고 답합니다.
2.  **파편화된 지식 (Knowledge Fragmentation)**: 사용자가 질문한 A는 DB에 있고 B는 DB에 없을 때, 시스템은 A에 대해서만 답하거나 비교 자체를 거부합니다. 사용자는 이미 알고 있는 B에 대한 일반 지식과 DB에 있는 A의 상세 정보를 융합한 답변을 기대합니다.
3.  **답변의 불투명성**: LLM이 가끔 필터를 뚫고 자신의 지식으로 답할 때가 있는데, 사용자는 이것이 DB에서 온 것인지 LLM의 상상(Hallucination)인지 구분할 방법이 없습니다.

## 🎯 요구사항 (Requirements)

### 1. Hybrid Reasoning (지식 융합 - Mixing Strategy)
- **전략**: DB 검색 결과(Retrieved Context)와 LLM의 내부 지식(Parametric Knowledge)을 **한 답변 내에서 혼합(Mix)**합니다.
- **방법**: RAG의 내용이 빈약하더라도 (예: 특정 수치나 최신 사실만 존재), 이를 답변의 '핵심 팩트'로 삼고, 앞뒤 맥락이나 보충 설명은 LLM의 지식으로 채워 풍부한 답변을 완성합니다.
- **제어**: LLM에게 "문맥에 정보가 있으면 절대적으로 문맥을 따르고(Verified Fact), 문맥에 없는 부분만 일반 지식으로 보강하라"는 명확한 우선순위를 부여합니다.

### 2. Granular Inline Citations (세밀한 출처 표기)
- 답변 내에서 특정 문장이나 구절이 DB의 어느 문서에서 왔는지 `[1]`, `[2]`와 같은 인라인 태그를 삽입합니다.
- **포맷**: `...이라는 분석이 있습니다[1]. 반면 일반적인 시장 상황에서 삼성은...` (전자는 DB 정보, 후자는 LLM 지식)

### 3. Knowledge Source Distinction (지식 출처 구분)
- 사용자가 답변을 읽을 때 **"번호가 달린 문단/문장은 내가 제공한 근거 데이터이고, 번호가 없는 나머지 맥락은 AI의 일반적인 상식이구나"**를 시각적으로 즉시 인지할 수 있도록 합니다.
- 이를 통해 RAG 데이터의 '희소하지만 강력한(Sparse but Powerful)' 특징을 극대화합니다.

### 4. Reference List (참조 목록)
- 답변 하단에 사용된 인덱스(`[1]`)에 대응하는 실제 문서의 제목과 URL을 클릭 가능한 링크 형태로 제공합니다.

## ✅ Acceptance Criteria (BDD Scenarios)

### Scenario 1: Full RAG Base Answer
- **Given**: 사용자 질문에 대응하는 충분한 정보가 DB(Context)에 존재할 때
- **When**: 답변을 생성하면
- **Then**: 모든 주요 정보에 인라인 Citation(`[1]`)이 붙고, 하단 Reference 리스트에 출처가 정확히 표기됨.

### Scenario 2: Hybrid Mixed Answer (Sparse but Powerful)
- **Given**: 질문의 일부(A)는 DB에 있고, 일부(B)는 없을 때
- **When**: 답변을 생성하면
- **Then**: A에 대한 설명에는 Citation이 붙고, B에 대한 설명은 Citation 없이 LLM의 지식으로 보강되어 자연스럽게 한 문단으로 출력됨.

### Scenario 3: Global Knowledge Fallback
- **Given**: 질문에 대한 정보가 DB에 전혀 없을 때 (Fallback 발생 시)
- **When**: 답변을 생성하면
- **Then**: "지식 베이스에 관련 정보가 없어 일반 지식을 바탕으로 답한다"는 안내와 함께 답변이 생성되며, Citation과 Reference 리스트는 나타나지 않음.

## 📈 Quality Gate
1. **Test Coverage**: RAG Node의 Citation 파싱 로직 유닛 테스트 Pass.
2. **Integration**: `tests/integration/bdd/test_hybrid_knowledge.py` 시나리오 Pass.
