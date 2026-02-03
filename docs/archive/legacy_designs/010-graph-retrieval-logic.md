# Design Guide 010: Graph Retrieval Logic Fix (Entity-based Search)

## 1. 배경 및 문제점 (Background & Problem)

### 1.1 현상
"일론 머스크와 트위터의 관계는?" 같은 질문을 했을 때, RAG 시스템이 Graph DB(Neo4j)에서 유의미한 정보를 가져오지 못하는 현상이 발생함.

### 1.2 원인 분석
현재 `GraphRetrieval` 로직(RAGService/Nodes)은 질문 문장 전체("일론 머스크와 트위터의 관계는?")를 임베딩하여 Vector Similarity Search를 수행하는 방식(Hybrid Search)에 의존하고 있음.

1. **Granularity Mismatch**: Neo4j에 저장된 노드는 "일론 머스크", "트위터", "인수"와 같이 단어/Entity 단위임. 질문 전체 문장의 임베딩 벡터와 Entity 노드의 임베딩 벡터 간의 유사도가 낮음.
2. **Missing Logic**: 질문에서 핵심 Entity를 추출하여 직접 그래프를 순회(Traversal)하는 로직이 부재함.

## 2. 해결 방안 (Solution Strategy)

Vector 유사도 기반 검색에서 **명시적 Entity 기반 검색(Keyword Match & Traversal)**으로 전환해야 함.

### 2.1 Logic Flow

1.  **Intent Classification & Entity Extraction**:
    *   `IntentClassifier` 단계에서 사용자의 질문 의도(Intent)뿐만 아니라 **관련 Entity 목록**을 추출한다.
    *   LLM에게 `entities: list[str]` 필드를 출력하도록 지시함.
    *   예: `{"intent": "relationship", "entities": ["일론 머스크", "트위터"]}`

2.  **Graph Traversal (Cypher Generation)**:
    *   추출된 Entity들을 Neo4j에서 조회(`MATCH (n) WHERE n.name IN [...]`)한다.
    *   Entity 노드들 사이의 직접적인 관계(`(a)-[r]-(b)`)를 탐색한다.
    *   필요 시 1-hop 이웃 노드나 공통 이웃 노드를 탐색 범위에 포함한다.

3.  **Context Injection**:
    *   탐색된 그래프 관계(예: `(일론 머스크)-[:ACQUIRED]->(트위터)`)를 자연어 텍스트나 정형화된 포맷으로 변환한다.
    *   기존 Vector DB 검색 결과와 병합하여 LLM Context에 주입한다.

## 3. 구현 상세 (Implementation Details)

### 3.1 `IntentClassifier` Prompt 수정
```python
class IntentResult(BaseModel):
    intent: str
    reasoning: str
    keywords: list[str] # 기존 검색어
    entities: list[str] = Field(default_factory=list, description="질문에 등장하는 주요 고유명사(인물, 조직 등)")
```

### 3.2 `Neo4jRepository.find_relationships` 추가
```cypher
MATCH (a:Entity), (b:Entity)
WHERE a.name IN $entities AND b.name IN $entities
MATCH p = shortestPath((a)-[*]-(b))
RETURN p
```
또는 단순 1-hop 조회:
```cypher
MATCH (n:Entity)-[r]-(m:Entity)
WHERE n.name IN $entities
RETURN n.name, type(r), m.name
```

## 4. Expected Effect
*   "A와 B의 관계"와 같은 질문에 대해 Graph DB의 강점인 **관계 정보**를 정확히 인출할 수 있음.
*   Vector Search가 놓치는 문맥(키워드 불일치)을 보완함.
