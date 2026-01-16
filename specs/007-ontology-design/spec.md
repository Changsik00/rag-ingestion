# Spec 007: Ontology Design (Multi-layered)

## 1. 개요 (Overview)

본 Spec은 **"의미에서 지식으로의 전환"**을 시작하는 단계입니다. Spec 005에서 추출된 비정형 Entity들(`entities: Dict[str, List[str]]`)을 **명확한 타입으로 분류**하고, 그들 간의 **관계 스키마를 설계**하여 향후 Knowledge Graph 구축의 **청사진(Blueprint)**을 완성합니다.

> **핵심 질문**: "Elon Musk와 Tesla는 어떤 관계인가?" → 이를 답하려면 먼저 "Elon Musk는 Person이고, Tesla는 Organization이다"라는 **타입 정의**가 필요합니다.

## 2. 목표 (Goals)

1. **Entity 타입 체계 확립**: 추출된 Entity를 목적별로 명확히 분류
2. **관계(Relationship) 스키마 설계**: Entity 간 의미 있는 연결고리 정의
3. **확장 가능한 구조**: 향후 새로운 Entity 타입 추가가 용이한 아키텍처
4. **문서화**: 왜 이런 타입과 관계를 선택했는지 설계 근거 명확히 기록

## 3. 상세 요구사항 (Requirements)

### 3.1 Entity 타입 분류 (Entity Type Taxonomy)

현재 Spec 005의 `entities` 필드는 다음과 같은 형태입니다:
```python
entities: Dict[str, List[str]] = {
    "Person": ["Elon Musk", "Sam Altman"],
    "Organization": ["Tesla", "OpenAI"],
    "Technology": ["Python", "Neo4j"],
    "Concept": ["Machine Learning", "Ontology"]
}
```

**문제점**:
- 타입 이름이 자유 형식 (Free-form string)
- LLM이 임의로 타입을 만들 수 있음 (예: "Tech" vs "Technology")
- 타입 간 계층 구조 없음 (예: "Technology"와 "Concept"의 경계 모호)

**해결 방안** (🎯 This Spec):
다음의 **표준 Entity 타입**을 정의하고, LLM이 반드시 이 중 하나로 분류하도록 강제합니다:

1. **`PERSON`**: 실존 인물 또는 캐릭터
   - 예: "Elon Musk", "Satoshi Nakamoto", "Geoffrey Hinton"
   
2. **`ORGANIZATION`**: 회사, 단체, 기관
   - 예: "Tesla", "Stanford University", "World Health Organization"
   
3. **`TECHNOLOGY`**: 구체적인 기술, 도구, 프레임워크, 언어
   - 예: "Python", "Neo4j", "GPT-4", "Docker"
   
4. **`CONCEPT`**: 추상적 개념, 이론, 방법론
   - 예: "Machine Learning", "Clean Architecture", "Ontology"
   
5. **`LOCATION`**: 지리적 위치
   - 예: "Seoul", "Silicon Valley", "United States"
   
6. **`EVENT`**: 특정 사건, 컨퍼런스, 역사적 순간
   - 예: "World War II", "OpenAI DevDay 2024"
   
7. **`ACTIVITY`**: 행위, 작업, 프로세스, 활동
   - 예: "책 쓰기", "벤치마킹", "코드 리뷰", "데이터 분석", "프로토타이핑"

**설계 결정**:
- Python `Enum`으로 정의하여 타입 안정성 확보
- LLM Prompt에 명시적으로 타입 목록 제공 (총 7개 타입)
- 분류 애매한 경우 `CONCEPT`를 폴백(Fallback)으로 사용

### 3.2 관계(Relationship) 스키마 설계

Entity만 있고 연결(Link)이 없으면 단순 태그 시스템에 불과합니다. **관계**를 통해 진짜 지식 그래프가 됩니다.

#### 3.2.1 Phase 1 관계 (✅ This Spec Scope)

**Document-Entity 관계** (가장 기본):
- `(:Document)-[:MENTIONS]->(:Entity)`
  - *의미*: "이 문서는 X를 언급한다"
  - *활용*: "Elon Musk를 언급한 모든 문서 찾기"

**Entity-Entity 관계** (향후 추론 가능):
현재는 **스키마만 정의**하고, 실제 추출은 Spec 008에서 구현:
- `(:Person)-[:WORKS_FOR]->(:Organization)`
- `(:Person)-[:FOUNDED]->(:Organization)`
- `(:Technology)-[:USED_BY]->(:Organization)`
- `(:Concept)-[:RELATED_TO]->(:Concept)`
- `(:Person)-[:PERFORMED]->(:Activity)` (예: "Elon Musk가 벤치마킹을 수행")
- `(:Technology)-[:SUPPORTS]->(:Activity)` (예: "Python이 데이터 분석을 지원")
- `(:Activity)-[:PART_OF]->(:Activity)` (예: "코드 리뷰는 개발 프로세스의 일부")

#### 3.2.2 고급 관계 (📅 Future Specs)

- `[:CONTRADICTS]`: 모순 관계 (Spec 009: Logic Resolver)
- `[:PRECEDES]`: 시간적 선후 관계
- `[:PART_OF]`: 계층 구조

### 3.3 스키마 정의 방식

**Option A: Neo4j Cypher Schema** (❌ 너무 빠른 구현)
- 장점: Neo4j에 바로 적용 가능
- 단점: Infrastructure에 종속, Domain 레이어 순수성 위반

**Option B: Pydantic Schema + Documentation** (✅ 채택)
- `app/domain/schemas/ontology.py` 생성
- Entity 타입과 관계를 Python 코드로 문서화
- 실제 Neo4j 매핑은 Spec 008에서 Infrastructure 레이어에서 처리

```python
# 예시 구조 (실제 구현은 plan.md 참조)
from enum import Enum

class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    # ...

class RelationshipType(str, Enum):
    MENTIONS = "MENTIONS"
    WORKS_FOR = "WORKS_FOR"
    # ...
```

## 4. 비-목표 (Non-Goals)

이번 Spec에서 하지 **않는** 것:
- ❌ 실제 Neo4j 노드/관계 생성 (Spec 008에서 진행)
- ❌ LLM이 Entity-Entity 관계 추출 (Spec 008에서 진행)
- ❌ Graph 탐색 API 개발 (Spec 008에서 진행)

**본 Spec의 역할**: **"설계도 작성"** - 데이터 구조와 규칙만 정의

## 5. 아키텍처 (Architecture)

### 5.1 레이어 구조

```
app/domain/schemas/
├── extraction.py          # ✅ 기존 (Spec 005)
└── ontology.py            # 🆕 (This Spec)
    ├── EntityType (Enum)
    ├── RelationshipType (Enum)
    └── EntityClassification (Pydantic Model)
```

### 5.2 통합 포인트

`ExtractedMetadata` 스키마 업데이트:
```python
# Before (Spec 005)
entities: Dict[str, List[str]]  # Free-form types

# After (Spec 007)
entities: Dict[EntityType, List[str]]  # Strongly typed
```

### 5.3 LLM Prompt 업데이트

LangChain Adapter의 프롬프트에 타입 목록 명시:
```
You must classify entities into EXACTLY one of these types:
- PERSON: Individual people or characters
- ORGANIZATION: Companies, institutions, groups
- ...
```

## 6. 성공 기준 (Acceptance Criteria)

1. ✅ `EntityType` Enum이 정의되고, 7개 타입 포함 (PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, LOCATION, EVENT, ACTIVITY)
2. ✅ `RelationshipType` Enum이 정의되고, 8개 관계 타입 포함 (MENTIONS, WORKS_FOR, FOUNDED, USES, RELATED_TO, PERFORMED, SUPPORTS, PART_OF)
3. ✅ `ExtractedMetadata.entities` 필드가 `Dict[EntityType, List[str]]`로 변경
4. ✅ LLM Prompt가 타입 제약을 포함하도록 업데이트
5. ✅ 기존 테스트가 새 스키마로 업데이트되어 pass
6. ✅ `docs/ontology.md` 문서 생성 (타입 정의 및 선택 근거 설명)

## 7. 설계 근거 (Design Rationale)

### 7.1 왜 지금 Ontology를 설계하는가?

- **데이터 정합성**: 타입 없이 Entity를 계속 쌓으면 나중에 "Python"이 언어인지 뱀인지 구분 불가
- **Graph 전 단계**: Neo4j에 넣기 전에 논리적 구조부터 잡아야 함
- **LLM 품질 향상**: 명확한 타입 지시로 추출 정확도 개선

### 7.2 왜 7개 타입인가?

- **Too Few**: Person, Organization만 있으면 "AI"같은 개념이나 "책 쓰기"같은 활동 분류 불가
- **Too Many**: 20개 타입은 LLM도 헷갈리고 유지보수 부담
- **Just Right**: 7개는 대부분의 지식(인물, 조직, 기술, 개념, 장소, 사건, 활동)을 커버하면서도 관리 가능

### 7.3 확장성 고려

- 새 타입 추가는 `EntityType` Enum에 값만 추가하면 됨
- 관계도 동일 방식으로 확장 가능
- 하위 타입 계층(예: `PROGRAMMING_LANGUAGE < TECHNOLOGY`)은 향후 고려

## 8. 리스크 및 완화 전략 (Risks & Mitigation)

| 리스크 | 영향 | 완화 전략 |
|--------|------|-----------|
| LLM이 타입을 잘못 분류 | Medium | 프롬프트에 예시 추가, Few-shot learning |
| 기존 데이터 호환성 깨짐 | Low | Migration script 작성 또는 Optional 처리 |
| 타입 경계 모호 (Tech vs Concept) | Medium | 문서에 명확한 가이드라인 작성 |

## 9. 후속 작업 (Follow-up)

- **Spec 008: Knowledge Graph Construction**
  - 이번 Spec에서 정의한 스키마를 Neo4j에 실제 구현
  - Entity-Entity 관계 추출 및 저장
  - Graph 탐색 API 개발

---

**문서 작성일**: 2026-01-16  
**작성자**: AI Agent (Antigravity)  
**승인자**: User (보류 중)
