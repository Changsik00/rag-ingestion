# Plan: Spec 007 - Ontology Design (Multi-layered)

## 📌 목표 (Goal)

Spec 005에서 자유 형식으로 추출되던 Entity 타입을 **표준화된 Enum**으로 강제하고, Entity 간 관계(Relationship) 스키마를 정의하여 향후 Knowledge Graph 구축을 위한 **데이터 계약(Data Contract)**을 확립합니다.

**핵심 변경점**:
- `Dict[str, List[str]]` → `Dict[EntityType, List[str]]` (타입 안정성 확보)
- Entity 타입 6종 & 관계 타입 4종 Enum 정의
- LLM Prompt에 타입 제약 명시

## ⚠️ User Review Required

> [!IMPORTANT]
> **Breaking Change**: `ExtractedMetadata.entities` 필드 타입 변경
> 
> 기존: `entities: Dict[str, List[str]]`  
> 변경: `entities: Dict[EntityType, List[str]]`
> 
> **영향 범위**:
> - Infrastructure 레이어의 LangChain Prompt 수정 필요
> - 기존 테스트 데이터 업데이트 필요
> - 이미 저장된 데이터는 호환되지 않으나, 새로운 데이터만 영향받음 (마이그레이션 불필요)

> [!WARNING]
> **LLM 정확도 리스크**: 타입 제약 추가로 초기에는 잘못된 분류 발생 가능
> 
> **완화 전략**:
> - Prompt에 Few-shot 예시 추가
> - 테스트 케이스로 분류 품질 검증
> - 필요 시 타입 정의 재조정

## 📝 Proposed Changes

### Domain Layer

#### [NEW] [ontology.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/ontology.py)

새로운 스키마 파일 생성:

```python
from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class EntityType(str, Enum):
    """표준화된 Entity 타입 분류"""
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    TECHNOLOGY = "TECHNOLOGY"
    CONCEPT = "CONCEPT"
    LOCATION = "LOCATION"
    EVENT = "EVENT"
    ACTIVITY = "ACTIVITY"

class RelationshipType(str, Enum):
    """Entity 간 관계 타입 (향후 Spec 008에서 활용)"""
    MENTIONS = "MENTIONS"              # Document -> Entity
    WORKS_FOR = "WORKS_FOR"            # Person -> Organization
    FOUNDED = "FOUNDED"                # Person -> Organization
    USES = "USES"                      # Organization -> Technology
    RELATED_TO = "RELATED_TO"          # Concept -> Concept
    PERFORMED = "PERFORMED"            # Person -> Activity
    SUPPORTS = "SUPPORTS"              # Technology -> Activity
    PART_OF = "PART_OF"                # Activity -> Activity

class TypedEntity(BaseModel):
    """Entity 분류 결과 (향후 확장용)"""
    name: str = Field(description="Entity 이름")
    type: EntityType = Field(description="Entity 타입")
    confidence: float = Field(default=1.0, description="분류 신뢰도")
```

**설계 근거**:
- `str` 기반 Enum으로 JSON 직렬화 용이
- `TypedEntity`는 향후 확장(신뢰도 추가 등)을 위한 준비

---

#### [MODIFY] [extraction.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/schemas/extraction.py)

`ExtractedMetadata` 스키마 업데이트:

```python
from app.domain.schemas.ontology import EntityType

class ExtractedMetadata(BaseModel):
    title: Optional[str] = Field(...)
    summary: str = Field(...)
    keywords: List[str] = Field(...)
    
    # ✨ 변경: 타입 안정성 확보
    entities: Dict[EntityType, List[str]] = Field(
        description="Extracted entities grouped by standardized type."
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Introduction to Vector Databases",
                "summary": "...",
                "keywords": [...],
                "entities": {
                    "TECHNOLOGY": ["ChromaDB", "Pinecone", "Python"],
                    "CONCEPT": ["High-dimensional space", "Embeddings"],
                    "PERSON": ["Geoffrey Hinton"],
                    "ORGANIZATION": ["Stanford AI Lab"],
                    "ACTIVITY": ["벤치마킹", "프로토타이핑"]
                }
            }
        }
    )
```

**변경 사유**: LLM이 임의 타입 생성 방지, 데이터 정합성 향상

---

### Infrastructure Layer

#### [MODIFY] [langchain_adapter.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/llm/langchain_adapter.py)

LLM Prompt에 타입 제약 추가:

```python
from app.domain.schemas.ontology import EntityType

EXTRACTION_PROMPT = """
Extract metadata from the following text.

**Entity Classification Rules**:
You MUST classify entities into EXACTLY one of these types:

- PERSON: Individual people or fictional characters
  Examples: "Elon Musk", "Geoffrey Hinton", "Steve Jobs"

- ORGANIZATION: Companies, institutions, or groups
  Examples: "Tesla", "MIT", "World Health Organization"

- TECHNOLOGY: Specific tools, frameworks, languages, or technical products
  Examples: "Python", "Docker", "GPT-4", "Neo4j"

- CONCEPT: Abstract ideas, theories, methodologies, or academic concepts
  Examples: "Machine Learning", "Clean Architecture", "Quantum Computing"

- LOCATION: Geographic locations, cities, regions, or countries
  Examples: "Seoul", "Silicon Valley", "United States"

- EVENT: Specific events, conferences, or historical moments
  Examples: "OpenAI DevDay 2024", "World War II", "AGI Summit"

- ACTIVITY: Actions, tasks, processes, or work activities
  Examples: "책 쓰기", "벤치마킹", "코드 리뷰", "데이터 분석", "프로토타이핑", "A/B 테스팅"

**Important**: If an entity could fit multiple types, prioritize based on context.
If uncertain, use CONCEPT as a fallback.

Text:
{text}

Output in JSON format matching ExtractedMetadata schema.
"""
```

**변경 사유**: 명확한 타입 지시로 LLM 분류 정확도 향상

---

### Tests

#### [MODIFY] [test_extractor.py](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/domain/test_extractor.py)

기존 테스트의 Mock 데이터를 새 스키마에 맞게 수정:

```python
from app.domain.schemas.ontology import EntityType

def test_extract_success():
    mock_llm = Mock(spec=LLMInterface)
    mock_llm.extract_metadata.return_value = ExtractedMetadata(
        title="AI Research and Development Practices",
        summary="Comprehensive guide on modern AI development",
        keywords=["AI", "Research", "Development"],
        entities={
            EntityType.PERSON: ["Geoffrey Hinton", "Yann LeCun"],
            EntityType.ORGANIZATION: ["Google DeepMind", "Meta AI"],
            EntityType.TECHNOLOGY: ["Python", "PyTorch", "TensorFlow"],
            EntityType.CONCEPT: ["Deep Learning", "Neural Networks"],
            EntityType.LOCATION: ["Silicon Valley", "Montreal"],
            EntityType.EVENT: ["NeurIPS 2024"],
            EntityType.ACTIVITY: ["벤치마킹", "모델 학습", "데이터 전처리"]
        }
    )
    # ... 나머지 테스트
```

---

#### [NEW] [test_ontology.py](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/domain/test_ontology.py)

새로운 테스트 파일 생성하여 Enum 검증:

```python
from app.domain.schemas.ontology import EntityType, RelationshipType
from app.domain.schemas.extraction import ExtractedMetadata

def test_entity_type_enum_values():
    """EntityType Enum이 7개 타입을 포함하는지 검증"""
    assert len(EntityType) == 7
    assert EntityType.PERSON.value == "PERSON"
    assert EntityType.ACTIVITY.value == "ACTIVITY"

def test_relationship_type_enum_values():
    """RelationshipType Enum이 8개 타입을 포함하는지 검증"""
    assert len(RelationshipType) == 8
    assert RelationshipType.PERFORMED.value == "PERFORMED"
    assert RelationshipType.SUPPORTS.value == "SUPPORTS"

def test_extracted_metadata_with_diverse_entities():
    """다양한 Entity 타입을 포함한 ExtractedMetadata 검증"""
    metadata = ExtractedMetadata(
        title="Startup Growth Strategy",
        summary="Analysis of startup scaling methods",
        keywords=["startup", "growth", "strategy"],
        entities={
            EntityType.PERSON: ["Eric Ries", "Steve Blank"],
            EntityType.ORGANIZATION: ["Y Combinator", "500 Startups"],
            EntityType.TECHNOLOGY: ["AWS", "React", "PostgreSQL"],
            EntityType.CONCEPT: ["Lean Startup", "Product-Market Fit"],
            EntityType.LOCATION: ["San Francisco", "Seoul"],
            EntityType.EVENT: ["TechCrunch Disrupt 2024"],
            EntityType.ACTIVITY: ["고객 인터뷰", "MVP 개발", "피벗팅"]
        }
    )
    assert EntityType.ACTIVITY in metadata.entities
    assert "고객 인터뷰" in metadata.entities[EntityType.ACTIVITY]
    assert len(metadata.entities) == 7  # 모든 타입 포함

def test_extracted_metadata_with_korean_activities():
    """한글 활동명이 올바르게 처리되는지 검증"""
    metadata = ExtractedMetadata(
        title="소프트웨어 개발 프로세스",
        summary="현대적인 개발 방법론",
        keywords=["개발", "프로세스"],
        entities={
            EntityType.ACTIVITY: [
                "책 쓰기", "벤치마킹", "코드 리뷰", 
                "페어 프로그래밍", "회고", "스프린트 계획"
            ]
        }
    )
    assert len(metadata.entities[EntityType.ACTIVITY]) == 6

def test_relationship_type_enum():
    """RelationshipType Enum 정의 검증"""
    assert RelationshipType.MENTIONS.value == "MENTIONS"
    assert RelationshipType.PERFORMED.value == "PERFORMED"
    assert RelationshipType.PART_OF.value == "PART_OF"
```

---

### Documentation

#### [NEW] [ontology.md](file:///Users/ck/Project/doit/rag-ingestion/docs/ontology.md)

Ontology 설계 문서 생성 (한글):

**목차**:
1. **배경 (Background)**: 왜 타입 체계가 필요한가?
2. **Entity 타입 정의**: 각 타입의 의미, 예시, 선택 기준
3. **Relationship 타입 정의**: 관계의 의미 및 활용 시나리오
4. **설계 결정 기록 (ADR)**:
   - 왜 6개 타입인가?
   - 왜 Pydantic Enum인가?
   - 확장성 고려 사항
5. **향후 계획**: Spec 008에서 어떻게 활용되는가?

---

## ✅ Verification Plan

### Automated Tests

#### 1. Unit Tests (Domain Layer)

**테스트 파일**: `tests/unit/domain/test_ontology.py` (신규)

**실행 명령어**:
```bash
pytest tests/unit/domain/test_ontology.py -v
```

**검증 항목**:
- ✅ `EntityType` Enum이 6개 값 포함
- ✅ `RelationshipType` Enum이 5개 값 포함
- ✅ `ExtractedMetadata`가 `Dict[EntityType, List[str]]` 타입 허용
- ✅ JSON 직렬화/역직렬화 정상 작동

#### 2. Existing Tests Update

**테스트 파일**: `tests/unit/domain/test_extractor.py` (수정)

**실행 명령어**:
```bash
pytest tests/unit/domain/test_extractor.py -v
```

**검증 항목**:
- ✅ 기존 테스트가 새 스키마로 업데이트되어 pass

#### 3. Integration Test (Optional)

**테스트 파일**: `tests/integration/test_api_ingest.py` (수정 필요 시)

**실행 명령어**:
```bash
pytest tests/integration/test_api_ingest.py -v
```

**검증 항목**:
- ✅ 실제 LLM 호출 시 타입 제약이 적용되는지 확인 (Mock 대신 실제 Gemini 호출)

### Manual Verification

#### 1. LLM Extraction 품질 확인

**목적**: 타입 제약 추가 후 실제 분류 정확도 검증

**실행 방법**:
```bash
# 기존 수동 검증 스크립트 활용
uv run python scripts/manual_verify_extraction.py
```

**확인 사항**:
1. 출력된 `entities` 필드의 키가 모두 Enum 값인지 확인 (예: `"TECHNOLOGY"`)
2. Entity 분류가 합리적인지 육안 검증 (예: "Python"이 TECHNOLOGY로 분류되는지)
3. 잘못 분류된 경우 Prompt 수정 필요성 판단

#### 2. API Response 검증

**실행 방법**:
```bash
# 서버 실행 (터미널에서 이미 실행 중)
# uv run uvicorn app.interfaces.api.main:app --reload

# 새 터미널에서 API 호출
curl -X POST "http://localhost:8000/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/tech-article"}'
```

**확인 사항**:
1. Response의 `entities` 필드 구조가 올바른지 확인
2. Swagger UI (`http://localhost:8000/docs`)에서 스키마 문서 확인

---

## 🧪 Test Execution Order

1. **Unit Tests (Domain)** → 가장 먼저 검증
2. **Unit Tests (Infrastructure)** → Prompt 업데이트 검증
3. **Integration Tests** → End-to-end 동작 확인
4. **Manual Verification** → 최종 품질 확인

---

## 📚 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Schema Definition | Pydantic `BaseModel` + `Enum` | 타입 안정성 및 직렬화 |
| LLM Integration | LangChain (LCEL) | Prompt 템플릿 관리 |
| Testing | pytest | Unit/Integration 테스트 |
| Documentation | Markdown | 설계 근거 문서화 |

---

## 🚀 Implementation Tasks (참고용)

실제 작업은 `task.md`에서 관리:

1. ✅ Spec 문서 작성 (`spec.md`)
2. ⏳ Plan 문서 작성 (`plan.md`) ← **현재 단계**
3. ⬜ Task 체크리스트 작성 (`task.md`)
4. ⬜ 사용자 리뷰 및 Plan Accept 대기
5. ⬜ Feature 브랜치 생성
6. ⬜ Domain/Infrastructure 구현
7. ⬜ 테스트 작성 및 검증
8. ⬜ PR 생성

---

**문서 작성일**: 2026-01-16  
**작성자**: AI Agent (Antigravity)  
**승인 대기 중**: User Review Required
