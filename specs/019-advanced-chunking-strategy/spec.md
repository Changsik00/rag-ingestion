# Spec 019: Advanced Chunking Strategy

## 📋 배경 및 문제 정의 (Background & Problem)
현재 시스템은 수집된 문서(AtomicDocument)를 단일 단위로 처리하거나 단순한 방식으로만 분할하고 있습니다.
이로 인해 긴 문서의 경우 임베딩 벡터가 문서의 구체적인 의미를 희석시키거나, 검색 시 정확도가 떨어지는 문제(Lost in the Middle)가 발생할 수 있습니다.
RAG 성능의 핵심인 정밀한 검색(Retrieval)을 위해, 문맥을 고려한 고급 청킹 전략(Recursive Character Splitting)과 Parent-Child 문서 구조 도입이 필요합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **Recursive Chunking with Overlap**: 
    - LangChain의 `RecursiveCharacterTextSplitter`를 도입하여 문서를 의미론적 단위(단락 -> 문장 -> 단어)로 분할한다.
    - **Chunk Overlap** 적용: 청크 간에 일정 길이(예: 200자)를 중복시켜, 청크 경계에서 문맥이 끊기는 문제를 방지하고 의미적 연속성을 보장한다.
2. **Configuration**: 청크 크기(Chunk Size)와 오버랩(Chunk Overlap)을 설정 파일(`env` 등) 또는 코드 상수(Default: 1000/200)로 관리한다.
3. **Structured Storage**:
    - **Neo4j**: 원본 문서(`Document`)와 분할된 청크(`Chunk`) 간의 관계(`:HAS_CHUNK`)를 그래프로 저장한다. (`(:Document)-[:HAS_CHUNK]->(:Chunk)`)
    - **ChromaDB**: 임베딩은 `Chunk` 단위로 생성 및 저장하며, 메타데이터에 원본 문서의 ID(`parent_id`), 순서(`index`), 그리고 오버랩 정보를 포함한다.
4. **Ingestion Pipeline Update**: `IngestionService`가 문서를 저장하기 전 `Chunker` 서비스를 통해 분할 과정을 거치도록 파이프라인을 수정한다.

### Non-Functional Requirements
1. **Performance**: 청킹 및 다량의 청크 저장으로 인한 인제스션 지연을 최소화해야 한다 (배치 처리 고려).
2. **Scalability**: 문서 하나당 수십~수백 개의 청크가 생성될 수 있으므로, DB 저장 로직이 이를 효율적으로 처리해야 한다.

## ✅ Definition of Done
1. API `/ingest/web`을 통해 긴 문서를 수집했을 때, Neo4j에 `Document`와 여러 개의 `Chunk` 노드가 생성되고 연결되어야 한다.
2. 생성된 청크들이 설정된 Overlap 길이만큼 이전/이후 청크와 중복된 텍스트를 포함하고 있어야 한다.
3. ChromaDB에 저장된 벡터 수가 생성된 청크 수와 일치해야 한다.
4. `IngestionService` 단위 테스트 및 통합 테스트(BDD)가 통과해야 한다.
