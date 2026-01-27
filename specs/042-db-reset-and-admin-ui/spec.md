# Spec 042: DB Reset Architecture & Admin UI

## 1. Background & Context
현재 RAG 파이프라인 개발 및 테스트 과정에서 데이터 정합성이 깨지는 문제(Data Drift)가 빈번하게 발생하고 있습니다. 특히 Neo4j(Graph)와 ChromaDB(Vector) 간의 데이터 불일치, 그리고 GraphState(SQLite)의 이전 대화 상태가 꼬이면서 테스트 효율이 저하되고 있습니다. 매번 Docker를 재시작하거나 DB 파일을 수동으로 지우는 것은 비효율적입니다.

## 2. Goals & Scope
개발자 및 관리자가 Admin UI에서 손쉽게 시스템 상태를 "초기화(Factory Reset)"하고, 테스트 도중 브라우저를 새로고침해도 대화 이력(History)이 유지되도록 하여 테스트 연속성을 보장하는 것이 목표입니다.

### 2.1 In-Scope
- **Admin API**: `POST /admin/integrity/reset` 엔드포인트 구현
  - Neo4j 데이터 전체 삭제 (`MATCH (n) DETACH DELETE n`)
  - ChromaDB 컬렉션 초기화 (`reset()` or `delete_collection`)
  - Checkpointer(SQLite) 상태 초기화
- **Admin UI**:
  - Sidebar에 "⚙️ System Management" (Danger Zone) 섹션 추가
  - "Reset All Data" 붉은색 버튼 및 확인(Double Confirm) 모달/로직
- **UX Improvement**:
  - Streamlit `st.session_state`를 활용한 Chat History 영속성 개선 (새로고침 시 증발 방지)

### 2.2 Out-of-Scope
- 프로덕션 레벨의 백업 및 복구(Backup & Restore)
- 사용자별 권한 관리 (현재는 단일 Admin 상정)

## 3. Detailed Requirements

### 3.1 DB Reset API (`/admin/integrity/reset`)
- **Method**: POST
- **Response**:
  ```json
  {
    "status": "success",
    "details": {
      "neo4j": "deleted 150 nodes",
      "chroma": "reset collection 'rag-collection'",
      "sqlite": "cleared checkpoints"
    }
  }
  ```
- **Safety**: 환경변수 `ENV=production` 일 경우 동작 거부 (Optional)

### 3.2 Streamlit Persistence
- **Problem**: Streamlit은 상호작용 시마다 전체 스크립트를 재실행하므로, `st.session_state`에 저장되지 않은 변수는 날아감. 브라우저 새로고침(F5) 시에는 세션 자체가 초기화될 수 있음.
- **Solution**:
  - `admin/4_RAG_Playground.py` 진입 시, Backend API(`GET /admin/history` - *New*)를 통해 이전 대화 내용을 불러오거나, 로컬 파일/DB에 저장된 History를 로드하는 구조 고려.
  - 또는 단순하게 `st.session_state`가 유지되는 동안은 탭 이동이나 단순 리런에도 대화가 유지되도록 로직 강화. (이번 Spec에서는 Session State 강화에 집중)

## 4. Key Deliverables
1. `app/interfaces/admin_api.py`: Reset API 구현
2. `app/application/admin/integrity_service.py`: 초기화 로직 (Facade Pattern)
3. `admin/4_RAG_Playground.py`: History 유지 로직 및 Reset UI 추가
4. `specs/042-db-reset-and-admin-ui/walkthrough.md`: UI 동작 검증 리포트

## 5. Constraints
- Neo4j 초기화 시 `apoc.periodic.iterate` 등을 사용하여 대량 데이터도 빠르게 삭제해야 함.
- 초기화 후에는 반드시 "시스템이 초기화되었습니다"라는 명시적 피드백을 UI에 노출.
