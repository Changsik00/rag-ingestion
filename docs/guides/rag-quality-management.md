# RAG Retrieval Quality & Context Management Guide

RAG 시스템에서 스크래핑 데이터와 불완전한 작업으로 인한 "DB 오염"은 성능을 급격히 저하시키는 고질적인 문제입니다. 특히 지식그래프(KG)와 벡터 DB를 병용할 경우, 잘못된 관계 정보는 'Hallucination'의 주범이 됩니다.

이 가이드는 데이터 정제 **가드레일(Prevention)**과 **사후 보정 서비스(Correction)**를 통해 최적의 컨텍스트를 LLM에게 제공하기 위한 운영 전략을 정의합니다.

---

## 0. 장애 사례 연구 (Incident Case Study)

### 일론 머스크 직책 정보 누락 건
*   **근본 원인 (Pollution Acceptance)**: 외부 데이터(Wikipedia)의 노이즈를 처리하는 과정에서 '안전한 보존'보다 '공격적 삭제'를 우선시함. 또한, 의미 없는 관계(`MENTIONS`)가 DB에 적재되는 것을 입구에서 차단하지 못함.
*   **기술적 교훈**: 
    - `{{Infobox}}`와 같은 구조화된 메타데이터는 텍스트 클리닝 대상에서 제외해야 함.
    - 지식 그래프는 단순 연결이 아닌 'Semantics(의미)'가 보장된 트리플만 수용해야 함.

---

## 1. 데이터 가드레일 (Prevention Strategy)

데이터가 DB에 들어가기 전, 'Minimum Viable Data(최소 유효 데이터)' 기준을 통과해야만 적재를 허용합니다.

### 📋 데이터 유효성 검증 레이어 (MVD)
- **필수 필드 검증**: 제목(`title`)과 본문(`content`)의 최소 길이(예: 50자)를 체크하며, Null/공백 필드는 즉시 Reject함.
- **정보 밀도(Information Density)**: 단어 수 대비 의미 있는 명사/엔티티 비율을 체크하여 저가치 데이터 적재 방지.
- **관계 무결성**: 지식그래프 트리플(S-P-O) 중 하나라도 비어 있거나 고립된 노드(Isolates)가 발생하는 경우 적재 중단.

### 🛠️ 트랜잭션 및 상태 관리
- **원자적 작업(Atomic Commits)**: 스크래핑-추출-임베딩-적재 과정을 하나의 트랜잭션으로 묶어, 중간 실패 시 전체 롤백.
- **체크포인트 시스템**: LangGraph의 Checkpointer를 활용해 작업 상태(Pending, Processing, Completed)를 기록하고, 중단 시 오염된 파편을 남기지 않도록 관리.

---

## 2. 데이터 보정 프로세스 (Correction Pipeline)

이미 적재된 오염 데이터를 식별하고 복구하는 워크플로우입니다.

### 🔍 단계별 보정 워크플로우
1.  **탐지 (Detection)**: Shadowing Query를 통해 본문이 짧거나 관계 연결이 1개 이하인 노드 식별.
2.  **분류 (Classification)**: LLM Quality Scoring을 통해 '삭제 대상'과 '보완 대상' 분류.
3.  **보완 (Enrichment)**: **Admin UI: Enrich Graph** 기능을 통해 해당 URL 재접속 및 데이터 재추출.
4.  **통합 (Merging)**: Entity Resolution을 통해 파편화된 노드(예: '삼성'과 '삼성전자') 통합.

### 🧹 그래프 DB 전용 정제
- **Dangling Edge 제거**: 목적지 없는 관계 주기적 삭제.
- **Centrality 분석**: 비정상적으로 높은 연결성을 가진 노드가 검색 결과를 왜곡하지 않도록 중심성 체크.

---

## 3. 추천 아키텍처: 스테이징 레이어 (Staging Area)

데이터를 Production DB에 바로 적재하지 않고, 중간 '검역소'를 두는 방식을 지향합니다.

1.  **Scraping Area**: 원본 데이터(Raw) 임시 저장.
2.  **Staging Area**: 유효성 검사, 중복 제거, LLM 기반 요약 및 태깅 수행.
3.  **Production DB**: 검증이 완료된 '깨끗한' 데이터만 벡터 및 그래프 DB로 전송.

---

## 4. 어드민 활용 및 모니터링
- **Context Preview**: LLM이 보게 될 정제된 텍스트를 상시 모니터링하여 Infobox 실시간 확인.
- **Drift 보고서**: Neo4j와 Chroma 간의 데이터 불일치 및 제목 누락 여부를 주기적으로 체크하여 일괄 보정 실행.

---

## 🚀 Future Backlog
- [ ] [RAG-001] MVD 검증 레이어 구현 (Ingestion Pipeline 통합)
- [ ] [RAG-002] LLM 기반 정보 가치 점수(Information Density) 평가 로직 도입
- [ ] [RAG-003] Entity Resolution (중복 노드 통합) 스크립트 작성

> [!IMPORTANT]
> 상세 구현 계획은 [.agent/backlog/rag-quality-bench.md](../../.agent/backlog/rag-quality-bench.md)를 참고하십시오.
