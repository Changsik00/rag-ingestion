# 실행 계획: Spec 052 - Clean Architecture 계층 정제

## 🎯 목표
Spec 051에서 남은 계층 경계 위반과 네이밍 불일치를 수정하여 Clean Architecture 원칙을 엄격히 준수합니다.

## 🗺️ 실행 전략

### Phase 1: 계층 경계 수정 (높은 우선순위)
잘못 배치된 인터페이스와 서비스를 올바른 아키텍처 계층으로 이동.

### Phase 2: 네이밍 표준화 (중간 우선순위)
일관성과 명확성을 위한 파일 및 클래스 이름 변경.

### Phase 3: 구조 정리 (낮은 우선순위)
불필요한 중첩 및 중복 파일 제거.

---

## 📋 작업 분해

### Task 1: 인터페이스 계층 마이그레이션

#### 1-1. LLM 인터페이스 마이그레이션
**파일:**
- `app/domain/interfaces/llm.py` → `app/application/interfaces/llm.py`

**영향 분석:**
```bash
grep -r "from app.domain.interfaces.llm" app/ tests/
```

**작업 단계:**
1. 필요시 `app/application/interfaces/` 디렉토리 생성
2. `llm.py`를 새 위치로 이동
3. 코드베이스 전체의 import 업데이트
4. 테스트 실행하여 검증

**예상 업데이트 파일 수:** ~15개

#### 1-2. Scraper 인터페이스 마이그레이션
**파일:**
- `app/domain/interfaces/scraper.py` → `app/application/interfaces/scraper.py`

**영향 분석:**
```bash
grep -r "from app.domain.interfaces.scraper" app/ tests/
```

**작업 단계:**
1. `scraper.py`를 `application/interfaces/`로 이동
2. 모든 import 업데이트
3. 테스트 실행

**예상 업데이트 파일 수:** ~8개

#### 1-3. Feedback 서비스 마이그레이션
**파일:**
- `app/domain/services/feedback.py` → `app/application/services/feedback.py`

**영향 분석:**
```bash
grep -r "from app.domain.services.feedback" app/ tests/
grep -r "app.domain.services.feedback" app/ tests/
```

**작업 단계:**
1. `feedback.py`를 `application/services/`로 이동
2. 모든 import 및 의존성 주입 업데이트
3. 테스트 파일 위치 업데이트
4. 테스트 실행

**예상 업데이트 파일 수:** ~10개

---

### Task 2: Value Object 재정리

#### 2-1. DocumentMetadata 마이그레이션
**파일:**
- `app/domain/models/document_metadata.py` → `app/domain/value_objects/document_metadata.py`

**영향 분석:**
```bash
grep -r "from app.domain.models.document_metadata" app/ tests/
```

**작업 단계:**
1. 파일을 `value_objects/`로 이동
2. Import 업데이트
3. `models/` 디렉토리가 비어있으면 제거 고려

**예상 업데이트 파일 수:** ~20개

---

### Task 3: 파일 및 클래스 이름 변경

#### 3-1. Admin Agent → Agent
**파일:**
- `app/application/services/admin_agent.py` → `app/application/services/agent.py`

**영향 분석:**
```bash
grep -r "admin_agent" app/ tests/
```

**작업 단계:**
1. 파일 이름 변경
2. 모든 import 업데이트
3. 테스트 파일 이름 업데이트 (존재 시)

**예상 업데이트 파일 수:** ~12개

#### 3-2. IngestionUseCase → Ingestion
**파일:**
- `app/application/services/ingestion.py` (클래스명만 변경)

**작업 단계:**
1. `IngestionUseCase` 클래스를 `Ingestion`으로 이름 변경
2. 모든 참조 업데이트
3. 의존성 주입 업데이트
4. 테스트 파일 이름 업데이트

**예상 참조 업데이트 수:** ~25개 파일

#### 3-3. Core 파일 단순화
**파일:**
- `app/core/utils/file_processor.py` → `app/core/file_processor.py`
- `app/core/logging_config.py` → `app/core/logger.py`

**작업 단계:**
1. `file_processor.py`를 한 레벨 위로 이동
2. `logging_config.py`를 `logger.py`로 이름 변경
3. `utils/` 디렉토리가 비어있으면 제거
4. 모든 import 업데이트

**예상 업데이트 파일 수:** ~15개

---

### Task 4: State 객체 정제

#### 4-1. State 파일 명확화를 위한 이름 변경
**파일:**
- `app/domain/ingestion/state.py` → `app/domain/ingestion/graph_state.py`
- `app/domain/rag/state.py` → `app/domain/rag/graph_state.py`

**근거:** 이들이 도메인 엔티티가 아닌 LangGraph 기술적 제약임을 명시적으로 표현.

**작업 단계:**
1. 파일 이름 변경
2. Import 업데이트
3. 테스트 실행

**예상 업데이트 파일 수:** ~10개

---

### Task 5: 중복 파일 정리

#### 5-1. 중복 파일 찾기 및 제거
**명령어:**
```bash
find app/interfaces/api -name "jobs.py"
find app/interfaces/api -name "*.py" -type f
```

**작업 단계:**
1. 중복 또는 고아 엔드포인트 파일 식별
2. 실제로 사용되지 않는지 확인 (import, git 히스토리 확인)
3. 중복 확인 시 제거
4. 테스트 실행

---

## 🧪 테스트 전략

### 작업별 테스트
각 파일 이동/이름 변경 후:
```bash
uv run pytest tests/unit/
uv run pytest tests/integration/
```

### 최종 검증
```bash
# 전체 테스트 스위트
uv run pytest

# 린팅
uv run ruff check .

# Import 검증
python -c "from app.application.services.agent import ConversationalRAGAgent"
python -c "from app.application.interfaces.llm import SemanticExtractor"
```

---

## 📊 위험도 평가

**높은 위험:**
- 인터페이스 마이그레이션 (많은 import 변경)
- IngestionUseCase 이름 변경 (광범위하게 사용됨)

**중간 위험:**
- File processor 경로 변경
- Admin agent 이름 변경

**낮은 위험:**
- State 파일 이름 변경
- Logger 이름 변경
- 중복 제거

---

## 🚀 실행 순서

1. **Task 1** (인터페이스): Clean architecture 준수에 중요
2. **Task 2** (Value Objects): Task 1의 의존성
3. **Task 3.2** (IngestionUseCase): 높은 영향도, 조기 실행
4. **Task 3** (기타 이름 변경): 낮은 위험
5. **Task 4** (State): 언제든지 가능
6. **Task 5** (정리): 마지막 단계

---

## ✅ 완료 정의

- [ ] 모든 파일이 올바른 아키텍처 계층으로 이동
- [ ] 모든 import 업데이트 및 검증
- [ ] 린팅 오류 0개
- [ ] 모든 테스트 통과 (194+ 테스트)
- [ ] PR 문서 완료
- [ ] 필요시 Design guide 업데이트
