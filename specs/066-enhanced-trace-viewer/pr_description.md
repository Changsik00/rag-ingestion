## Summary
Spec 066에서는 RAG 파이프라인의 Rerank 투명성을 확보하기 위해 상세 로그 수집 및 시각화 기능을 구현했습니다. 

## Key Review Points
- `app/application/services/rag.py`: `RAGResult` 엔티티 확장
- `app/infrastructure/ai/rag_nodes.py`: Pointwise Reranking 상세 로그(score, reasoning) 수집 로직 추가
- `admin/pages/3_Observability_&_Trace.py`: Rerank Analysis 시각화 탭 구현
- `admin/pages/4_RAG_Playground.py`: Trace 링크 버튼 추가

## Checklist
- [x] RAGResult 및 State에 rerank_log 반영
- [x] Rerank Node 로그 생성 로직 구현
- [x] Admin UI 시각화 탭 추가
- [x] Playground 내 Trace 이동 버튼 추가
