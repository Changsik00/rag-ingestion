# PR Description: Spec 055 RAG Precision & Advanced Settings

## 📌 Summary
Spec 055의 구현 사항인 "RAG 정밀도 향상 및 고급 설정" 기능을 추가했습니다.
API 엔드포인트의 입력 구조를 강화하고, Admin UI에서 검색 파라미터(Top-K, Temperature, Strategy)를 직접 제어할 수 있도록 개선했습니다.

## 🔄 Changes
- **API**: `POST /ask` 엔드포인트가 `ChatRequest` DTO를 사용하도록 변경 (Breaking Change).
    - `advanced_settings` 필드 추가: `top_k`, `temperature`, `search_strategy` 지원.
- **DTO**: `ChatRequest`, `AdvancedSettings` Pydantic 모델 정의 및 Validation 로직 추가.
- **Admin UI**: RAG Playground에 "Advanced Settings" Expander 추가.
    - 슬라이더 및 라디오 버튼을 통한 파라미터 튜닝 UI 구현.

## 🧪 Verification
- **Unit Test**: `tests/unit/interfaces/api/v1/dto/test_rag_dto.py` (New)
    - DTO Validation 및 Default Value 테스트 완료.
- **Integration Test**: `tests/integration/functional/test_api_endpoints.py` (Updated)
    - `test_rag_ask_flow`: 정상 요청(202) 확인.
    - `test_rag_ask_validation_error`: 잘못된 파라미터(Top-K=0)에 대한 422 에러 반환 확인.

## ⚠️ Notes
- `ChatRequest` 도입으로 인해 `ask_agent` 엔드포인트의 Payload 스키마가 변경되었습니다.
- 기존 클라이언트가 `dict` 기반으로 호출하던 코드는 `ChatRequest` 구조(JSON)에 맞춰 수정이 필요할 수 있습니다 (현재는 Admin UI가 유일한 클라이언트라 영향 없음).
