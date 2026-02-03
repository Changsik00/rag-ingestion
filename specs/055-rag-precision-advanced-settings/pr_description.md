# feat(spec-055): rag precision and advanced settings

## 📋 Summary

### 배경 및 목적
기존 RAG Playground는 검색 및 생성 파라미터가 고정되어 있어, 정확도 문제 발생 시 디버깅이 어렵고 다양한 유즈케이스에 대응하기 힘들었습니다.
본 작업(Spec 055)은 검색 품질(Precision) 제어 및 고급 튜닝을 위해 **API 입력 구조를 개선**하고 **Admin Dashboard에 제어 패널을 추가**하는 것을 목적으로 합니다.

### 주요 변경 사항
- [x] **API DTO 도입**: `ChatRequest` 및 `AdvancedSettings` Pydantic 모델을 도입하여 입력값 검증 강화 (Spec 053 잔여 과제 해결).
- [x] **고급 설정 지원**: Top-K, Temperature, Search Strategy(Hybrid/Vector/Keyword) 파라미터 지원.
- [x] **UI 고도화**: Admin Dashboard에 "Advanced Settings" Expander를 추가하여 실시간 튜닝 환경 제공.

## 🎯 Key Review Points
1.  **Breaking Change**: `POST /ask` 엔드포인트의 Payload 스키마가 `dict`에서 `ChatRequest` 구조로 변경되었습니다.
2.  **Config Injection**: LangGraph 실행 시 `configurable` 딕셔너리를 통해 `retrieval_config`가 올바르게 주입되는지 로직 확인이 필요합니다.
3.  **Validation**: `top_k=0` 등 유효하지 않은 값에 대해 API가 422 에러를 정상적으로 반환하는지 확인해 주세요.

## 🧪 Verification

### Automated Tests
```bash
# Unit Tests (DTO Validation)
uv run pytest tests/unit/interfaces/api/v1/dto/test_rag_dto.py

# Integration Tests (API Endpoint)
uv run pytest tests/integration/functional/test_api_endpoints.py
```
**테스트 결과 요약:**
- ✅ `test_rag_dto.py`: 필드 검증 및 기본값 테스트 통과.
- ✅ `test_api_endpoints.py`: 정상 요청(202) 및 에러 케이스(422) 테스트 통과.

### Manual Verification (Scenarios)
1.  **Dashboard 접속**: `uv run streamlit run admin/Home.py` 실행 후 RAG Playground 접속.
2.  **Advanced Settings 확인**: 사이드바 하단(또는 메인 화면)의 "Advanced Settings" Expander 확장.
3.  **파라미터 변경 테스트**:
    - Top-K를 1로 설정하고 질문 → 답변과 함께 표시되는 Reference 문서가 1개인지 확인.
    - Strategy를 "Reference Only" 등으로 변경해보고 동작 확인 (현재 Hybrid 기본).
4.  **Swagger UI 검증**: `/docs` 접속 → `POST /rag/sessions/{id}/ask` 스키마가 `ChatRequest`로 표시되는지 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/interfaces/api/v1/dto/rag.py`: `ChatRequest`, `AdvancedSettings` DTO 정의.
- `tests/unit/interfaces/api/v1/dto/test_rag_dto.py`: DTO Unit Tests.

### 🛠 Modified Files
- `app/interfaces/api/v1/endpoints/rag.py`: `ask_agent` 시그니처 변경 및 Config 주입 로직 추가.
- `admin/pages/4_RAG_Playground.py`: Advanced Settings UI 위젯 추가 및 API 연동.
- `tests/integration/functional/test_api_endpoints.py`: 통합 테스트 케이스 업데이트.

**Total:** 5 files changed

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
