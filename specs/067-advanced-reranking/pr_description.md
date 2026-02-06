# PR Description: Spec-067 Advanced Reranking Logic

## 🎯 목적
Rerank 노드의 성능을 고도화하여 정보 파편화 문제를 해결하고, 청크 간 상대적 중요도를 반영한 최적의 컨텍스트 구성을 지원합니다.

## 🛠 주요 변경 사항
1. **Listwise 전략 도입**: 기존 Pointwise 방식의 한계를 보완하기 위해 여러 청크를 한 그룹으로 묶어 LLM이 상대적 순위를 비교하도록 함.
2. **Sliding Window (Context Expansion)**: 개별 청크의 전후 인접 청크를 로드하여 병합 분석함으로써 누락된 정보나 맥락을 복원.
3. **Repository 확장**: Neo4j에서 인접 청크를 빠르게 가져오기 위한 `get_adjacent_chunks` 메서드 구현.
4. **State 유연성 보장**: `RAGGraphState`에 `rerank_strategy`를 추가하여 런타임에 리랭킹 전략을 변경할 수 있도록 설계.

## 🧪 테스트 방법
- Trace Viewer 또는 Admin UI에서 `rerank_log`와 `reasoning_log`를 통해 선택된 전략과 리랭킹 결과 확인.

## 🔗 관련 문서
- [spec.md](file:///Users/ck/Project/doit/rag-ingestion/specs/067-advanced-reranking/spec.md)
- [plan.md](file:///Users/ck/Project/doit/rag-ingestion/specs/067-advanced-reranking/plan.md)
- [walkthrough.md](file:///Users/ck/Project/doit/rag-ingestion/specs/067-advanced-reranking/walkthrough.md)
