# [Spec-064 Extension] Admin UI: Trace Viewer & LangFuse Dashboard

## 📋 Goal
사용자가 "로그를 볼 수 있는 UI"를 요청함에 따라, 기존 `3_Trace_Viewer.py`를 개선하여 **LangFuse Dashboard**로의 연결성을 강화하고, 내부 LangGraph 상태 확인 기능과 통합합니다.

## 🛠 Proposed Changes

### `admin/pages/3_Trace_Viewer.py`
- **Page Title**: "Trace Viewer" -> "📊 Observability & Trace" 로 변경.
- **Section 1: External Observability (LangFuse)**
  - `LANGFUSE_HOST` 환경변수를 읽어 LangFuse 대시보드 바로가기 버튼 제공.
  - "모든 로그와 상세 트레이스는 LangFuse에서 확인할 수 있습니다" 안내 문구 추가.
- **Section 2: Internal State Inspection (LangGraph)**
  - 기존 `Analyze Trace` 기능 유지 (LangGraph Checkpointer 상태 확인용).

## 🧪 Verification Plan
1. **Scenario A (With LangFuse)**
   - `.env`에 LangFuse 설정이 있을 때.
   - UI 상단에 "🚀 Open LangFuse Dashboard" 버튼 표시 확인.
   - 클릭 시 설정된 `LANGFUSE_HOST`로 이동 확인.

2. **Scenario B (Without LangFuse)**
   - 설정이 없을 때 안내 문구("LangFuse is not configured") 출력 확인.
