# 구현 계획: Clean Architecture Refactoring

## 목표

Domain 레이어를 외부 의존성으로부터 격리하여 엄격한 Clean Architecture 달성

---

## Phase 1: LLM 인터페이스 추상화

### 1.1 Domain Interface 정의

**[NEW]** `app/domain/interfaces/llm.py`

```python
from typing import Protocol
from app.domain.schemas.extraction import ExtractedMetadata

class LLMInterface(Protocol):
    """LLM 추상 인터페이스 - Domain 레이어용"""
    
    def extract_metadata(self, text: str) -> ExtractedMetadata | None:
        """
        텍스트에서 구조화된 메타데이터 추출
        
        Args:
            text: 분석할 원본 텍스트
            
        Returns:
            ExtractedMetadata: 추출된 메타데이터 (실패 시 None)
        """
        ...
```

**설계 포인트**:
- Python `Protocol`: 덕 타이핑 기반 인터페이스
- 반환 타입: Domain 스키마(`ExtractedMetadata`)만 의존
- 구현체는 Infrastructure에서 제공

---

## Phase 2: Infrastructure Adapter 구현

### 2.1 LangChain Adapter 생성

**[NEW]** `app/infrastructure/llm/__init__.py`
```python
from .langchain_adapter import LangChainLLMAdapter

__all__ = ["LangChainLLMAdapter"]
```

**[NEW]** `app/infrastructure/llm/langchain_adapter.py`

```python
import logging
from typing import Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.schemas.extraction import ExtractedMetadata

logger = logging.getLogger(__name__)

class LangChainLLMAdapter:
    """LangChain을 LLMInterface에 맞게 변환하는 어댑터"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ExtractedMetadata)
        self.prompt = PromptTemplate(
            template=\"\"\"
            You are an advanced AI assistant capable of analyzing text and extracting structured metadata.
            
            Please analyze the following text and extract:
            1. A suitable title (if the original is missing or unclear).
            2. A concise summary (approx. 3 sentences).
            3. A list of 5-10 relevant keywords.
            4. Key entities classified by type (Person, Organization, Technology, Topic, etc.).
            
            Focus on capturing the core meaning and most important entities.
            
            Text to analyze:
            {text}
            
            {format_instructions}
            \"\"\",
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | self.parser
    
    def extract_metadata(self, text: str) -> Optional[ExtractedMetadata]:
        """LLMInterface 구현: 메타데이터 추출"""
        try:
            logger.info("Starting semantic extraction via LLM...")
            result = self.chain.invoke({"text": text})
            logger.info("Semantic extraction completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Failed to extract semantic metadata: {e}")
            return None
```

**설계 포인트**:
- 기존 `SemanticExtractor`의 LangChain 로직을 그대로 이동
- `LLMInterface` Protocol 구현 (덕 타이핑)
- Infrastructure 레이어에 위치

---

## Phase 3: Domain Service 단순화

### 3.1 SemanticExtractor 리팩토링

**[MODIFY]** `app/domain/services/semantic_extractor.py`

```python
import logging
from typing import Optional
from app.domain.interfaces.llm import LLMInterface
from app.domain.schemas.extraction import ExtractedMetadata

logger = logging.getLogger(__name__)

class SemanticExtractor:
    """도메인 서비스: 텍스트 메타데이터 추출 오케스트레이션"""
    
    def __init__(self, llm: LLMInterface):
        """
        Args:
            llm: LLM 인터페이스 구현체 (Infrastructure에서 주입)
        """
        self.llm = llm
    
    def extract(self, text: str) -> Optional[ExtractedMetadata]:
        """
        텍스트에서 메타데이터 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            ExtractedMetadata: 추출된 메타데이터 (실패 시 None)
        """
        return self.llm.extract_metadata(text)
```

**변경 사항**:
- ❌ LangChain 의존성 제거
- ❌ Core 레이어 의존성 제거
- ✅ `LLMInterface` Protocol만 의존
- ✅ 순수 비즈니스 로직만 유지

---

## Phase 4: Core & DI 업데이트

### 4.1 LLM Factory 수정

**[MODIFY]** `app/core/llm.py`

```python
from typing import Optional
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from functools import lru_cache
from dotenv import load_dotenv

from app.infrastructure.llm import LangChainLLMAdapter

load_dotenv()

class LLMFactory:
    @staticmethod
    @lru_cache()
    def get_google_llm(model: str = "gemini-2.0-flash-exp", temperature: float = 0.0) -> ChatGoogleGenerativeAI:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key
        )
    
    @staticmethod
    @lru_cache()
    def get_llm_adapter() -> LangChainLLMAdapter:
        """LangChain Adapter 반환"""
        llm = LLMFactory.get_google_llm()
        return LangChainLLMAdapter(llm)

def get_llm() -> LangChainLLMAdapter:
    """Adapter 반환 (DI용)"""
    return LLMFactory.get_llm_adapter()
```

### 4.2 의존성 주입 업데이트

**[MODIFY]** `app/interfaces/api/dependencies.py`

```python
# (변경 없음 - get_llm()이 이미 Adapter를 반환하므로)
@lru_cache
def get_semantic_extractor() -> SemanticExtractor:
    llm_adapter = get_llm()  # LangChainLLMAdapter 반환
    return SemanticExtractor(llm=llm_adapter)
```

---

## Phase 5: 테스트 업데이트

### 5.1 단위 테스트 개선

**[MODIFY]** `tests/unit/domain/test_extractor.py`

```python
import pytest
from unittest.mock import MagicMock
from app.domain.services.semantic_extractor import SemanticExtractor
from app.domain.schemas.extraction import ExtractedMetadata
from app.domain.interfaces.llm import LLMInterface

def test_extract_success():
    # Setup: Protocol Mock
    mock_llm = MagicMock(spec=LLMInterface)
    expected_metadata = ExtractedMetadata(
        title="Test Title",
        summary="Test Summary",
        keywords=["k1", "k2"],
        entities={"Person": ["Tester"]}
    )
    mock_llm.extract_metadata.return_value = expected_metadata
    
    # Execute
    extractor = SemanticExtractor(llm=mock_llm)
    result = extractor.extract("Dummy text")
    
    # Verify
    assert result is not None
    assert result.title == "Test Title"
    mock_llm.extract_metadata.assert_called_once_with("Dummy text")

def test_extract_failure():
    # Setup
    mock_llm = MagicMock(spec=LLMInterface)
    mock_llm.extract_metadata.return_value = None
    
    # Execute
    extractor = SemanticExtractor(llm=mock_llm)
    result = extractor.extract("Dummy text")
    
    # Verify
    assert result is None
```

**개선 사항**:
- ✅ Mock이 더 단순해짐 (Protocol 기반)
- ✅ LangChain 의존성 제거

---

## 변경 파일 요약

### 새로 생성
- `app/domain/interfaces/llm.py`
- `app/infrastructure/llm/__init__.py`
- `app/infrastructure/llm/langchain_adapter.py`

### 수정
- `app/domain/services/semantic_extractor.py`
- `app/core/llm.py`
- `tests/unit/domain/test_extractor.py`

### 삭제
- 없음

---

## 검증 계획

### 1. 단위 테스트
```bash
uv run pytest tests/unit/domain/test_extractor.py -v
```

### 2. 통합 테스트
```bash
uv run python scripts/manual_verify_extraction.py
```

### 3. 전체 테스트
```bash
uv run pytest
```

---

## 롤백 계획

변경이 문제 발생 시:
```bash
git revert HEAD~N  # N: 커밋 개수
```

또는 전체 롤백:
```bash
git checkout main
git branch -D refactor/clean-architecture
```
