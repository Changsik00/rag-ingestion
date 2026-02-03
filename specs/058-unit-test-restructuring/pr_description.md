# refactor(spec-058): unit test restructuring & stability upgrade

## 📋 Summary

### 배경 및 목적
최근 시스템의 기능 확장(Spec 055, 056)으로 인해 유닛 테스트 인터페이스가 변경됨에 따라 발생한 테스트 실패를 해결하고, Clean Architecture 계층 구조에 맞춰 테스트 디렉토리를 재배치하여 유지보수성을 극대화합니다. 또한 테스트 오딧을 통해 중복을 제거하고 커버리지를 보완했습니다.

### 주요 변경 사항

#### 1. 테스트 안정화 및 품질 정제 (Stability & Quality)
*   **인터페이스 정합성**: `RAGNodes` 호출 시 `RunnableConfig` 누락 문제를 해결하고, `ainvoke` 기반의 최신 Assert 로직으로 전환했습니다.
*   **중복 제거 및 통합**: 
    *   `test_rag_nodes_spec044.py` → `test_rag_nodes.py`로 통합.
    *   `test_usecases.py` → `test_ingestion.py`로 통합.
*   **안정성 강화**: `SemanticChunker` 테스트 시 실제 임베딩 API 호출을 방지하기 위해 `GoogleGenerativeAIEmbeddings`를 Mocking 처리했습니다.

#### 2. 계층형 테스트 구조 재편 (Restructuring)
`app/` 소스 코드의 **4-Layer Architecture** 위계를 `tests/unit/` 디렉토리에 1:1로 반영했습니다.

| 계층 | 상세 분류 | 주요 작업 내역 |
|:---:|:---|:---|
| **Infrastructure** | `repositories`, `factories`, `scrapers`, `rag`, `chunker` | 파편화된 인프라 구현체 테스트를 기능별 폴더로 격리 |
| **Domain** | `entities`, `services`, `value_objects` | 도메인 로직 및 VO 검증 로직 강화 |
| **Application** | `services` | 유스케이스 및 오케스트레이션 테스트 이동 |
| **Interfaces** | `api/v1`, `mcp` | API DTO 및 외부 인터페이스 테스트 체계화 |

#### 3. 신규 테스트 커버리지 (Coverage Expansion)
*   **RAG 전략 분기**: `search_strategy`(`vector`, `graph`, `hybrid`)에 따른 레포지토리 호출 로직 검증.
*   **VO 유효성 검사**: `ChunkingConfig` 등 주요 Value Object의 기본값 및 필드 유효성 테스트 추가.
*   **에러 핸들링**: 인제스션 파이프라인 단계별(Chunking 등) 장애 발생 시 Job 상태 전이 검증.

## 🎯 Key Review Points
1. **Directory Mapping**: 소스 코드 하위 구조와 일치하도록 재편된 테스트 경로 검토.
2. **Mocking Logic**: `SemanticChunker`의 임베딩 Mocking 방식 및 `RAGNodes`의 `llm.bind()` 모킹 적절성.

## 🧪 Verification

### Automated Tests
```bash
# 전체 유닛 테스트 실행
uv run pytest tests/unit
```
**테스트 결과 요약:**
* ✅ **164 passed** (기존 대비 6개 테스트 추가/정제 완료)
* 🛠 `TypeError` 및 실제 API 호출 위험 요소 전수 제거 확인.

### Code Quality
* ✅ `uv run ruff check . --fix` 실행: 이동된 파일들의 임포트 경로 자동 교정 완료.
* ✅ `uv run ruff format .` 실행: 컨벤션 통일 완료.

## ✅ Definition of Done
- [x] 모든 단위 테스트 통과 (164/164)
- [x] 중복 테스트 제거 및 통합 완료
- [x] Clean Architecture 기반 디렉토리 재배치 완료
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 업데이트 완료
- [x] Ruff lint 및 format 확인 완료
