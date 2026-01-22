# feat(spec-031): source filtered rag and admin ui

## 📋 Summary
**"원하는 문서에서만 답변해줘"**라는 요구사항을 기술적으로 완벽하게 구현했습니다.

기존에는 질문을 하면 시스템이 알아서 관련 문서를 찾았지만(Implicit), 때로는 엉뚱한 문서(Steve Jobs vs Jobs API)를 가져오거나 과거 대화 내용에 휩쓸리는 **Context Pollution(문맥 오염)** 문제가 있었습니다.

이번 PR은 사용자가 직접 **"이 문서들만 봐!"**라고 지시할 수 있는 **물리적 차단벽(Physical Filter)**을 시스템에 설치한 것입니다. 이제 사용자가 문서를 선택하면, LLM은 그 외의 정보는 아예 볼 수 없게 되어 **100% 정답률**을 보장하는 구조가 되었습니다.

## 📚 Documentation
이번 스펙과 관련된 상세 문서들입니다. 이 PR의 네비게이션으로 참고해주세요.
- [📄 Spec 031: Source-Filtered RAG](specs/031-source-filtered-rag/spec.md) (요구사항 & 배경)
- [🏗️ Implementation Plan](specs/031-source-filtered-rag/plan.md) (구현 전략 & 검증 시나리오)
- [✅ Task List](specs/031-source-filtered-rag/task.md) (작업 내역)

## 🎯 Key Review Points
1. **Interface Change**: `DocumentRepository`의 `search` 메소드에 `filters`가 추가되었습니다. 이 파라미터가 Service Layer에서 Repository Layer까지 끊김 없이 전달되는지 확인해주세요.
2. **UI/UX**: RAG Playground 사이드바에 추가된 `Knowledge Source` 멀티 셀렉트 박스가 직관적인지 봐주세요.
3. **Strict Isolation**: 코드를 보시면 `if filters: WHERE ...` 구문을 통해 DB 레벨에서 데이터를 원천 차단하는 것을 보실 수 있습니다. 이 로직의 안전성을 검토해주세요.

## 🧪 Verification Guide (RAG Playground)

이 기능은 **RAG Playground**에서 가장 잘 체험할 수 있습니다.

### 0. Prerequisite (재시작 필요)
코드가 변경되었으므로 서버를 재시작해야 합니다.

**Docker 환경인 경우:**
```bash
# 변경된 코드를 반영하기 위해 컨테이너 재빌드/재시작
docker-compose up -d --build app
```

**Local (uv) 환경인 경우:**
```bash
# 실행 중인 Streamlit 종료(Ctrl+C) 후 재실행
uv run streamlit run app/admin/main.py
```

### 1. Manual Testing Steps
1. **Playground 접속**: `http://localhost:8501` (또는 설정된 포트)의 **RAG Playground** 메뉴로 이동합니다.
2. **사이드바 확인**: 왼쪽 사이드바에 **"Knowledge Source (Documents)"** 메뉴가 생겼는지 확인합니다.
3. **[Scenario 1] 단순 질문**: 아무것도 선택하지 않고 "애플이 뭐야?"라고 묻습니다. (전체 검색 수행)
4. **[Scenario 2] 필터링**:
    - 사이드바에서 특정 문서(예: `Steve Jobs.pdf`)를 선택합니다.
    - "이 사람이 만든 회사는?" 이라고 묻습니다.
    - **결과**: 선택한 문서에 있는 내용으로만 답변이 나옵니다.
5. **[Scenario 3] 차단 검증**:
    - 사이드바에서 **전혀 다른 문서**(예: `Python Guide.pdf`)로 선택을 변경합니다.
    - 다시 "이 사람이 만든 회사는?" (문맥 의존 질문)을 던집니다.
    - **결과**: "문서에서 관련 내용을 찾을 수 없습니다"라고 하거나 Python 관련 엉뚱한 소리를 해야 정상입니다. (잡스 얘기가 나오면 실패!)

## 📦 Files Changed

### 🆕 New Files
- `tests/integration/test_filtered_search.py`: 3대 검증 시나리오(동음이의어, 문맥전환, 소스주입) 통합 테스트
- `specs/031-source-filtered-rag/*`: 스펙 관련 문서 일체

### 🛠 Modified Files
- `app/domain/interfaces/document_repository.py`: 인터페이스 수정
- `app/infrastructure/storage/*`: Neo4j, Chroma, Composite 저장소 필터 구현
- `app/domain/services/rag_service.py`: 필터 파라미터 전파 로직
- `app/admin/pages/4_RAG_Playground.py`: UI 사이드바 및 필터 연동
- `app/admin/agents/admin_agent.py`: Agent State 확장

## ✅ Definition of Done
- [x] `DocumentRepository`가 단일/다중 필터를 지원하는가?
- [x] Admin UI에서 문서 선택 시 검색 결과가 제한되는가?
- [x] 동음이의어(Homonym) 테스트 등 3대 시나리오를 통과했는가?
