## 💡 Title: feat(spec-063): admin ui/ux improvements

## 🚀 Summary
Spec 063에 따라 Admin Dashboard의 사용성을 개선했습니다.
1. **Verification Lab 추가**: RAG 파이프라인을 테스트할 수 있는 독립 페이지(`5_Verification_Lab.py`)를 추가했습니다.
2. **Graph Explorer 개선**: 프리셋 로딩 버그를 수정하고, 다크 모드에서의 가시성(Node/Edge Color)을 개선했습니다.
3. **Feedback UI 개선**: 피드백 버튼의 API 성공 여부 확인 로직을 추가했습니다.

## 📋 Changes
- `admin/pages/5_Verification_Lab.py`: 신규 페이지 생성.
- `admin/pages/1_Graph_Explorer.py`: Session State Key 적용 및 컬러 팔레트 조정.
- `admin/pages/4_RAG_Playground.py`: Feedback API Robustness 강화.
- `admin/utils/di_helper.py`: Admin 환경용 수동 Dependency Injection 헬퍼 추가.

## 🧪 Verification
- [x] **Lab 동작 확인**: `get_manual_rag_service`를 통한 RAG 실행 성공.
- [x] **Graph Visibility**: Dark Mode에서의 Edge 가시성 확보.
- [x] **Code Quality**: `uv run ruff check admin/` Pass.
