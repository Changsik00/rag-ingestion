# Spec 063: Admin UI/UX & Feature Review

## 1. Background
Admin Dashboard는 현재 기능 중심의 MVP 상태로, 사용자 경험(UX) 측면에서 몇 가지 불편함이 존재합니다. 특히 Graph Explorer의 다크 모드 가시성 문제와 프리셋 기능 동작 오류는 빈번한 사용 불편을 초래하고 있습니다. 또한, 터미널에서 실행하던 검증 스크립트(`manual_rag_verification.py`)를 UI로 통합하여 접근성을 높일 필요가 있습니다.

## 2. Goals
1.  **Verification Lab UI 구축**: `verify_llm.py` (실제로는 `scripts/manual_rag_verification.py`)의 기능을 Streamlit 페이지로 이식하여, Admin UI에서 직접 RAG 응답 품질을 테스트할 수 있게 한다.
2.  **Graph Style 개선**: Streamlit Dark Mode 환경에서 Node Label 및 Edge의 가시성을 확보한다.
3.  **Saved Query (Preset) 버그 수정**: 프리셋 로드 시 Text Area에 쿼리가 즉시 반영되지 않는 문제를 해결한다.
4.  **User Feedback 연동**: Chat Interface의 좋아요/싫어요 버튼을 백엔드 API와 연동한다.

## 3. Implementation Details
- **API**: `POST /feedback` (User Feedback API가 없다면 신설 필요, 현재 스코프 확인 필요)
    - *Note*: 현재 백엔드에 Feedback API가 있는지 확인 필요. 없다면 Mocking하거나 간단한 로깅으로 구현.

## 4. Work Mode
- **Mode**: SDD (Spec-Driven Development)
- **Reviewer**: User
