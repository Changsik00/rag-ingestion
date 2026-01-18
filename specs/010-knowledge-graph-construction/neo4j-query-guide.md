# Neo4j Graph 시각화 가이드

## 🎯 목적

Neo4j Browser를 사용하여 Knowledge Graph를 시각적으로 탐색하고 Cypher 쿼리로 분석하는 방법

---

## 🚀 Neo4j Browser 접속

### 1. Docker Compose 실행 확인
```bash
docker compose ps

# neo4j 컨테이너가 running 상태여야 함
```

### 2. Neo4j Browser 접속
```
브라우저에서: http://localhost:7474
```

### 3. 로그인
```
Username: neo4j
Password: password
```

**💡 Tip:** `docker-compose.yml`에서 비밀번호 확인 가능

---

## 📊 자주 사용하는 Cypher 쿼리

### 1️⃣ 전체 Graph 개요 보기
```cypher
# Database 통계
CALL db.schema.visualization()
```

### 2️⃣ Entity와 Document 관계 시각화
```cypher
# Document-Entity MENTIONS 관계 보기 (50개 제한)
MATCH (d:Document)-[r:MENTIONS]->(e:Entity)
RETURN d, r, e
LIMIT 50
```

**결과:** 노드와 관계가 그래프로 시각화됨! 마우스로 드래그하여 탐색 가능

### 3️⃣ 특정 Entity 주변 탐색
```cypher
# "Elon Musk"가 언급된 모든 Document
MATCH (e:Entity {name: "Elon Musk"})<-[r:MENTIONS]-(d:Document)
RETURN e, r, d
```

### 4️⃣ Entity 타입별 통계
```cypher
# Entity Type별 개수
MATCH (e:Entity)
RETURN e.type as EntityType, count(e) as Count
ORDER BY Count DESC
```

결과 예시:
```
EntityType     | Count
---------------|------
PERSON         | 25
ORGANIZATION   | 18
TECHNOLOGY     | 12
```

### 5️⃣ 가장 많이 언급된 Entity Top 10
```cypher
MATCH (e:Entity)<-[:MENTIONS]-(d:Document)
RETURN e.name, e.type, count(d) as mentions
ORDER BY mentions DESC
LIMIT 10
```

### 6️⃣ 특정 Document의 모든 Entity
```cypher
MATCH (d:Document {id: "your-doc-id"})-[:MENTIONS]->(e:Entity)
RETURN d.id, e.name, e.type
```

### 7️⃣ Entity 검색 (부분 일치)
```cypher
# "Musk"가 포함된 Entity 찾기
MATCH (e:Entity)
WHERE e.name CONTAINS "Musk" OR e.normalized_name CONTAINS "musk"
RETURN e.name, e.type
```

### 8️⃣ 전체 노드 및 관계 개수
```cypher
# 통계 확인
MATCH (n)
RETURN 
  labels(n)[0] as NodeType, 
  count(n) as Count
ORDER BY Count DESC
```

---

## 🎨 Graph 시각화 팁

### Neo4j Browser 기능

1. **노드 클릭** - 속성 상세 보기
2. **노드 더블클릭** - 연결된 노드 확장
3. **관계 클릭** - 관계 속성 보기
4. **우클릭** - 컨텍스트 메뉴 (숨기기, 고정 등)

### 시각화 커스터마이징

**색상 및 크기 설정:**
- 좌측 하단: Node 스타일 설정
- Entity type별 색상 지정 가능
- 크기를 mention count로 설정 가능

---

## 🔍 디버깅 쿼리

### 1. Entity 노드 확인
```cypher
MATCH (e:Entity)
RETURN e.name, e.type, e.normalized_name, e.created_at
LIMIT 20
```

### 2. MENTIONS 관계 확인
```cypher
MATCH (d:Document)-[r:MENTIONS]->(e:Entity)
RETURN d.id, e.name, r.created_at
LIMIT 20
```

### 3. 고아 노드 찾기 (관계 없는 Entity)
```cypher
MATCH (e:Entity)
WHERE NOT (e)<-[:MENTIONS]-()
RETURN e.name, e.type
```

### 4. 중복 Entity 확인
```cypher
MATCH (e:Entity)
WITH e.name as name, collect(e) as entities
WHERE size(entities) > 1
RETURN name, size(entities) as duplicates
```

---

## 📈 분석 쿼리

### Entity 공출현 분석
```cypher
# 같은 Document에 함께 언급된 Entity 쌍
MATCH (e1:Entity)<-[:MENTIONS]-(d:Document)-[:MENTIONS]->(e2:Entity)
WHERE id(e1) < id(e2)
RETURN e1.name, e2.name, count(d) as co_occurrences
ORDER BY co_occurrences DESC
LIMIT 20
```

### Document 길이 vs Entity 개수
```cypher
MATCH (d:Document)-[:MENTIONS]->(e:Entity)
WITH d, count(e) as entity_count
RETURN 
  entity_count,
  count(d) as document_count
ORDER BY entity_count
```

---

## 🗑️ 유틸리티 쿼리

### 전체 Entity 삭제 (주의!)
```cypher
MATCH (e:Entity)
DETACH DELETE e
```

### 특정 Entity 삭제
```cypher
MATCH (e:Entity {name: "Tesla"})
DETACH DELETE e
```

### MENTIONS 관계만 삭제
```cypher
MATCH ()-[r:MENTIONS]->()
DELETE r
```

---

## 🚨 주의사항

### 1. 대규모 쿼리
```cypher
# ❌ LIMIT 없이 전체 조회 (느림!)
MATCH (n) RETURN n

# ✅ LIMIT 사용
MATCH (n) RETURN n LIMIT 100
```

### 2. 성능 최적화
```cypher
# Index 사용 권장
MATCH (e:Entity {name: "Elon Musk"})  # ← name에 unique constraint 있음
```

### 3. Transaction 크기
- 대량 삭제/수정 시 `CALL {} IN TRANSACTIONS` 사용

---

## 🔗 참고 링크

- [Neo4j Cypher 공식 문서](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j Browser 가이드](https://neo4j.com/docs/browser-manual/current/)

---

## 💡 실전 예시

### Scenario: "AI 관련 문서 찾기"
```cypher
MATCH (e:Entity)<-[:MENTIONS]-(d:Document)
WHERE e.name CONTAINS "AI" OR e.name CONTAINS "LLM"
RETURN DISTINCT d.id, d.source_url
LIMIT 10
```

### Scenario: "특정 인물과 관련된 기술"
```cypher
MATCH (person:Entity {type: "PERSON"})<-[:MENTIONS]-(d)-[:MENTIONS]->(tech:Entity {type: "TECHNOLOGY"})
WHERE person.name = "Elon Musk"
RETURN DISTINCT tech.name, count(d) as mentions
ORDER BY mentions DESC
```

---

**작성일:** 2026-01-18  
**관련 파일:** 
- `app/infrastructure/storage/cypher_queries.py`
- `specs/010-knowledge-graph-construction/graph-schema-explained.md`
