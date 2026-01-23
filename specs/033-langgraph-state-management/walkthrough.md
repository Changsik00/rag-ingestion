# Walkthrough: Spec 033 - LangGraph State Management

LangGraph를 사용하여 RAG 파이프라인의 제어 흐름(Nervous System)을 구축하고, 상태 기반의 의사결정 체계를 완성했습니다.

## 🚀 주요 성과

1.  **3-Layer Architecture 완성**: Brain(의도), Nervous System(흐름), Body(검색) 레이어의 격리를 통해 유지보수성 향상.
2.  **State Management**: `RAGGraphState`를 통해 파이프라인의 모든 중간 과정(Intent, Filters, Chunks)을 명시적으로 관리.
3.  **병렬 검색 및 비동기 처리**: `asyncio.to_thread`와 `gather`를 사용하여 Vector, Keyword, Graph 검색을 동시 수행하여 성능 최적화.
4.  **HITL 기반 확보**: `SqliteSaver`를 연동하여 대화 상태 스냅샷 저장 및 향후 중단/재개 가능한 구조 마련.

## 🧪 테스트 및 트러블슈팅 결과

### 시나리오 1: 일반 질문 (Context Awareness)
- **질문**: "인공지능이 뭐야?" → "일론 머스크는?"
- **결과**: **성공**. 주어가 없는 후속 질문에서도 맥락을 파악하여 쿼리를 재작성함.
- **학습**: 지식 베이스에 정보가 없을 경우 할루시네이션 없이 "정보가 없다"고 응답하는 방어 동작 확인.

### 시나리오 2 & 3: 비교 질문 및 필터링 이슈 (Lessons Learned)
- **질문**: "Claude와 GPT-4 비교", "일론 머스크와 스티브 잡스의 공통점"
- **발견된 필터링 한계**: 
    - **언어/명칭 불일치**: Intent는 한국어 타겟("일론 머스크")을 뽑았으나 DB의 메타데이터(`source`)와 일치하지 않아 검색 결과가 0건이 됨.
    - **엄격한 매칭**: 자동 필터가 너무 강력하게 작동하여 관련 정보를 차단하는 부작용 확인.
- **LLM 폴백**: 컨텍스트가 없을 때 LLM이 자신의 내부 지식으로 답변하는 현상 관찰 (수정이 필요함).

## 🛠 향후 과제 (Spec 034 이관)
- **Filtering Robustness**: 필터 결과 0건 시 자동으로 전역 검색으로 전환하는 Fallback 로직 구현.
- **Query Expansion**: 추출된 대상을 검색 쿼리에 포함시켜 검색 확률 제고.

---

## 📸 실행 스크린샷

![Comparison Issue Screenshot](https://github.com/Changsik00/rag-ingestion/assets/placeholder_comparison_empty.png)
> 필터 불일치로 인해 Context가 비어있는 상태에서 LLM이 답변하는 모습 (Spec 034에서 개선 예정)
