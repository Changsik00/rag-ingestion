# RAG Retrieval Quality & Context Management Guide

이 가이드는 RAG(Retrieval-Augmented Generation) 시스템의 답변 품질을 유지하고 최적의 컨텍스트를 LLM에게 제공하기 위한 운영 지침입니다.

## 1. 컨텍스트 노이즈 제어 (Noise Cleaning)
- **Infobox 보존**: 위키백과와 같은 정형화된 데이터 소스에서 `{{Infobox ...}}` 템플릿은 핵심 사실(직책, 장소, 일자 등)을 포함합니다. 이를 절대 삭제하지 않도록 주의하십시오.
- **제거 대상**: 시스템은 답변 생성에 방해되는 `{{Navbox}}`, `{{Cite}}`, `[[파일:...]]` 등 시각적/참조용 요소만 제거합니다.
- **검증**: `nodes.py`의 `_clean_context_noise` 로직 수정 시 반드시 기존 단위 테스트를 통과해야 합니다.

## 2. 지식 그래프 정제 (Knowledge Graph Context)
- **Semantics 우선**: LLM에게 전달되는 그래프 팩트는 `WORKS_FOR`, `FOUNDED`와 같은 의미적 관계여야 합니다. 
- **Noise 필터링**: 단순 데이터 연결용인 `MENTIONS` 관계는 LLM의 집중력을 흐트러뜨리므로 컨텍스트 구성 시 필터링해야 합니다.

## 3. 어드민 도구를 활용한 품질 보정
- **Context Preview**: Storage Management에서 실제 LLM이 보게 될 정제된 텍스트를 상시 모니터링하십시오.
- **Semantic Re-extraction**: 특정 문서의 그래프 팩트가 부족하거나 잘못되었다면 'Re-extract' 기능을 통해 지식 추출을 재실행할 수 있습니다.

---

## 🚀 Future Backlog: Automated Quality Benchmarks
정기적으로 RAG 품질을 자동 측정하기 위한 벤치마크 테스트 도입이 필요합니다.
- [ ] [RAG-001] 위키 Infobox 보존 여부 자동 검증 테스트 구현
- [ ] [RAG-002] 그래프 컨텍스트 노이즈(MENTIONS) 필터링 검증
- [ ] [RAG-003] 주요 엔티티(인물, 조직) 대상 Retrieval 성능 측정 (Recall/Precision)

> [!TIP]
> 상세 구현 계획은 `.agent/backlog/rag-quality-bench.md`를 참고하십시오.
