# Spec 017: Embedding Strategy Refactoring

## 📋 배경 및 문제 정의

### 현재 상황
Spec 016 (Entity-Entity Relationship Extraction) 완료 후, ChromaDB embedding 관련 이슈로 4개의 integration test가 실패하고 있습니다.

### 문제점
1. **Heavy ML Dependencies**: ChromaDB가 로컬 all-MiniLM-L6-v2 모델을 사용하여 다음 의존성이 필요:
   - `onnxruntime>=1.16.0`
   - `tokenizers>=0.15.0`
   
2. **Docker 환경 이슈**: Docker 환경에서 onnxruntime을 찾지 못해 embedding 실패
   ```
   Error: Cannot find onnxruntime in Docker container
   ```

3. **컨테이너 비대화**: ML 라이브러리로 인해 Docker 이미지 크기 증가 및 빌드 시간 지연

4. **테스트 실패**: 다음 4개 integration test 실패
   - `test_successful_entity_graph_auto_construction` (test_knowledge_graph.py)
   - `test_entity_based_document_search` (test_knowledge_graph.py)
   - `test_entity_deduplication` (test_knowledge_graph.py)
   - `test_duplicate_url_sequential_ingestion` (test_high_priority_scenarios.py)

### 목표
- **Primary**: ChromaDB embedding 전략을 API 기반으로 전환하여 로컬 ML 의존성 제거
- **Secondary**: Docker 환경 경량화 및 안정화
- **Outcome**: 4개 실패 테스트 모두 통과

---

## 🎯 요구사항

### Functional Requirements
1. ChromaDB embedding을 외부 API 기반으로 전환
2. 4개 실패 테스트 모두 통과
3. 기존 Document 저장/조회 기능 유지

### Non-Functional Requirements
1. Docker 이미지 크기 감소
2. 빌드 시간 단축
3. Embedding 품질 유지 또는 개선

---

## 🔍 Embedding 전략 옵션 분석

### Option A: Gemini Embedding API ⭐ **추천**
**장점**:
- 이미 Gemini API 사용 중 (LangChain-Google-GenAI 연동)
- 추가 의존성 불필요
- 일관된 생태계 (같은 provider)
- Free tier 제공 (text-embedding-004)

**단점**:
- API 호출 비용 (Free tier 초과 시)
- 외부 API 의존성

**적용 방법**:
```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GEMINI_API_KEY")
)
```

### Option B: OpenAI Embedding API
**장점**:
- 고품질 embedding (text-embedding-3-small, text-embedding-3-large)
- 안정적인 서비스

**단점**:
- 새로운 API 키 필요
- 추가 의존성 (`langchain-openai`)
- 비용 (Free tier 없음)

### Option C: 경량 로컬 모델 (Sentence Transformers)
**장점**:
- 외부 API 없이 독립 운영

**단점**:
- 여전히 ML 의존성 필요
- Docker 이미지 여전히 비대
- 근본 문제 미해결

### 추천: **Option A (Gemini Embedding API)**
- 현재 프로젝트와 가장 잘 맞음
- 최소한의 변경으로 문제 해결
- 비용 효율적 (Free tier)

---

## 📦 영향 범위

### 변경 파일
1. **app/infrastructure/storage/chroma.py**
   - ChromaDB 초기화 시 embedding function 설정
   
2. **pyproject.toml**
   - `onnxruntime` 제거
   - `tokenizers` 제거

3. **Dockerfile** (필요 시)
   - ML 라이브러리 설치 명령 제거

### 영향받는 테스트
- `tests/integration/bdd/test_knowledge_graph.py` (3개 테스트)
- `tests/integration/bdd/test_high_priority_scenarios.py` (1개 테스트)

---

## ✅ Definition of Done

1. ChromaDB가 Gemini Embedding API 사용하도록 설정
2. `onnxruntime`, `tokenizers` 의존성 제거
3. 4개 실패 테스트 모두 통과
4. 전체 테스트 스위트 통과 (기존 통과 테스트 회귀 없음)
5. Docker 환경에서 정상 작동 확인
6. 문서화 (`docs/` 업데이트 필요 시)
