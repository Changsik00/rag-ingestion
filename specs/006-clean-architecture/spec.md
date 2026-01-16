# Refactor: Clean Architecture Improvement

## 개요

Domain 레이어를 외부 프레임워크(LangChain, Core)로부터 완전히 격리하여 **엄격한 Clean Architecture** 준수

## 배경

Spec 005(Basic Semantic Extraction) 구현 후 아키텍처 검토 결과:
- ✅ 전체 레이어 분리는 잘 되어 있음
- ⚠️ Domain이 `app/core/llm.py`에 의존
- ⚠️ Domain이 LangChain에 직접 의존

이는 **실용적 Clean Architecture**로는 허용되지만, 더 엄격한 Clean Architecture를 위해 개선이 필요합니다.

## 목표

### 주요 목표
1. **Domain 레이어 격리**: 외부 프레임워크 의존성 제거
2. **추상화 강화**: Python Protocol을 활용한 인터페이스 정의
3. **Infrastructure 분리**: LangChain 로직을 Infrastructure로 이동
4. **테스트 개선**: 더 단순한 Mock 작성 가능

### 비목표
- 기능 변경 없음 (Refactoring만)
- 백로그 스펙과 독립적 (문서 업데이트 불필요)

## 현재 문제점

### 1. Domain → Core 의존성
```python
# app/domain/services/semantic_extractor.py
from app.core.llm import get_llm  # ← Core 레이어 의존
```

### 2. Domain → LangChain 의존성
```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
```

**문제**:
- Domain이 LangChain에 강하게 결합
- LangChain → 다른 LLM 교체 시 Domain 수정 필요
- 단위 테스트에서 LangChain Mock 필요

## 해결 방안

### 1. LLM Interface 추상화 (Protocol)

**[NEW]** `app/domain/interfaces/llm.py`
```python
from typing import Protocol
from app.domain.schemas.extraction import ExtractedMetadata

class LLMInterface(Protocol):
    def extract_metadata(self, text: str) -> ExtractedMetadata | None:
        """텍스트에서 메타데이터 추출"""
        ...
```

**장점**:
- Domain은 추상 인터페이스만 의존
- 구체적 구현은 Infrastructure에서 제공

### 2. LangChain Adapter (Infrastructure)

**[NEW]** `app/infrastructure/llm/langchain_adapter.py`
- LangChain 로직을 Infrastructure로 이동
- `LLMInterface` 구현체로 동작

### 3. SemanticExtractor 단순화

**[MODIFY]** `app/domain/services/semantic_extractor.py`
```python
class SemanticExtractor:
    def __init__(self, llm: LLMInterface):  # Protocol 의존
        self.llm = llm
    
    def extract(self, text: str) -> ExtractedMetadata | None:
        return self.llm.extract_metadata(text)
```

## 예상 효과

### Clean Architecture 준수도

| 항목 | 이전 | 개선 후 |
|------|------|---------|
| Domain 격리 | 70% | 100% |
| 추상화 활용 | 80% | 100% |
| 테스트 용이성 | 70% | 100% |
| 프레임워크 교체 | 어려움 | 쉬움 |

### 테스트 개선
```python
# Before: LangChain Mock 필요
mock_chain = MagicMock()
mock_chain.invoke.return_value = expected_metadata

# After: 간단한 Protocol Mock
mock_llm = MagicMock(spec=LLMInterface)
mock_llm.extract_metadata.return_value = expected_metadata
```

## 검증 계획

### 1. 단위 테스트
- ✅ 기존 `test_extractor.py` 통과
- ✅ Mock 코드 단순화

### 2. 통합 테스트
- ✅ `scripts/manual_verify_extraction.py` 정상 동작

### 3. 전체 테스트
- ✅ `pytest` 전체 통과

## 관련 문서

- [Spec 005: Basic Semantic Extraction](../005-semantic-extraction/spec.md)
- [Clean Architecture Documentation](../../docs/architecture/)
