# refactor(spec-058): unit test restructuring & stability upgrade

## 📋 Summary

### 배경 및 목적
최근 시스템의 기능 확장(Spec 055, 056)으로 인해 유닛 테스트 인터페이스가 변경됨에 따라 발생한 테스트 실패를 해결하고, Clean Architecture 계층 구조에 맞춰 테스트 디렉토리를 재배치하여 유지보수성을 극대화합니다.

### 주요 변경 사항

#### 1. 테스트 안정화 (Stability Update)
*   **RAGNodes 인터페이스 정합성**: `retrieve_hybrid`, `generate_answer` 호출 시 `RunnableConfig` 인자가 누락되어 발생하던 `TypeError`를 해결했습니다.
*   **Mocking 고도화**: 
    *   `llm.bind()` 메서드가 동일한 LLM 인터페이스를 반환하도록 모킹하여 체인 실행 시의 런타임 오류를 방지했습니다.
    *   `agenerate` 대신 최신 인터페이스인 `ainvoke`를 사용하는 테스트 리서션으로 모두 전환했습니다.
*   **실패 케이스 수정**: `tests/unit/infrastructure/rag/test_rag_nodes.py`, `test_rag_reranker.py`, `test_rag_nodes_spec044.py` 등 총 7개의 깨진 테스트를 정상화했습니다.

#### 2. 계층형 테스트 구조 재편 (Restructuring)
`app/` 소스 코드의 **4-Layer Architecture** 위계를 `tests/unit/` 디렉토리에 1:1로 반영했습니다.

| 계층 | 상세 분류 | 주요 작업 내역 |
|:---:|:---|:---|
| **Infrastructure** | `repositories`, `factories`, `scrapers`, `rag`, `chunker` | 파편화된 인프라 구현체 테스트를 기능별 폴더로 격리 |
| **Domain** | `entities`, `services`, `value_objects` | 도메인 로직 및 VO 검증 로합성 강화 |
| **Application** | `services` | 유스케이스 및 오케스트레이션 테스트 이동 |
| **Interfaces** | `api/v1`, `mcp` | API DTO 및 외부 인터페이스 테스트 체계화 |

## 🎯 Key Review Points
1. **Directory Mapping**: 
   ```bash
   tests/unit/
   ├── application/services/
   ├── domain/entities/ | services/
   ├── infrastructure/repositories/ | rag/ | factories/ | scrapers/ | chunker/
   └── interfaces/api/ | mcp/
   ```
   위와 같이 재편된 구조가 소스 코드와의 동기화 측면에서 적절한지 검토 부탁드립니다.
2. **Import Integrity**: 파일 이동 후 `ruff --fix`를 통해 자동 교정된 임포트 경로에 이상이 없는지 확인 바랍니다.

## 🧪 Verification

### Automated Tests
```bash
# 전체 유닛 테스트 실행
uv run pytest tests/unit
```
**테스트 결과 요약:**
* ✅ **158 passed** (0 failed, 7 fixed)
* 🛠 `TypeError` 발생하던 노드 기반 테스트 전수 정상화 완료.

### Code Quality
* ✅ `uv run ruff check . --fix` 실행: 82개의 임포트/스타일 오류 자동 교정 완료.
* ✅ `uv run ruff format .` 실행: 컨벤션 통일 완료.

## 📦 Files Changed
*파일 이동 및 구조 변경 위주*

- `tests/unit/infrastructure/rag/test_rag_nodes.py`: 안정성 수정
- `tests/unit/application/test_rag_nodes_spec044.py`: 정합성 수정
- `tests/unit/infrastructure/test_rag_reranker.py`: 검증 로직 수정
- (기타 15+ 파일): 위치 이동 및 임포트 경로 수정

## ✅ Definition of Done
- [x] 모든 단위 테스트 통과 (158/158)
- [x] Clean Architecture 기반 디렉토리 재배치 완료
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료 (Walkthrough 내용 반영)
- [x] Ruff lint 및 format 확인 완료
