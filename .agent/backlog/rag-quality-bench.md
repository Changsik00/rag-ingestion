# Backlog: RAG Quality Benchmark Automation

## Overview
RAG 답변 품질의 회귀(Regression)를 방지하기 위해 정기적이고 자동화된 품질 측정이 필요합니다.

## Tasks

### [RAG-001] 위키 Infobox 보존 테스트
- **Goal**: `_clean_context_noise`가 중요한 Infobox 데이터를 삭제하지 않는지 검증.
- **Spec**: 다양한 위키 템플릿(Infobox, Navbox, Cite)이 섞인 샘플 데이터셋 구축 및 테스트 코드 작성.

### [RAG-002] 그래프 컨텍스트 정제 테스트
- **Goal**: 그래프 기반 답변 생성 시 `MENTIONS`와 같은 메타데이터 관계가 LLM 컨텍스트에 포함되지 않는지 검증.
- **Spec**: 특정 엔티티의 멀티-홉 관계를 시뮬레이션하고 최종 페이로드 검사.

### [RAG-003] 하이브리드 리트리벌 성능 측정
- **Goal**: 특정 질문에 대해 Vector + Keyword + Graph가 최적의 조합을 찾아내는지 측정.
- **Spec**: 정답 셋(Ground Truth)이 포함된 Q&A 쌍을 기반으로 Recall@K 측정.

## Related Documents
- [RAG Quality Management Guide](../../docs/guides/rag-quality-management.md)
