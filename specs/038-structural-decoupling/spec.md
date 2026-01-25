# Spec-038: Structural Decoupling (Streamlit & Backend Separation)

## 📋 배경 및 문제 정의 (Background & Problem)

현재 시스템은 Streamlit Admin UI가 백엔드 비즈니스 로직 및 데이터베이스(Neo4j, ChromaDB)에 직접 의존하고 있습니다. 이는 다음과 같은 아키텍처적 문제를 야기합니다.

1.  **계층 분리 위반**: UI 레이어가 데이터 액세스 레이어에 직접 접근하여 Clean Architecture 원칙을 위반합니다.
2.  **배포 유연성 저하**: UI와 API 서버를 독립적으로 확장하거나 배포하기 어렵습니다.
3.  **정합성 관리의 어려움**: 여러 경로(UI, API)에서 직접 DB를 조작함으로써 데이터 정합성 유지 및 보안 정책 적용이 파편화됩니다.

이를 해결하기 위해 Admin 전용 기능을 관리하는 Backend API Layer를 구축하고, Streamlit은 이 API만 호출하는 'Thin Client' 형태로 전환해야 합니다.

## 🎯 요구사항 (Requirements)

### 1. Functional Requirements: The 100% Decoupled API Blueprint

To achieve zero imports from `app/` to `admin/`, the following API suite must be fully implemented and utilized.

#### [Module 1] Job Management (Page 0)
- `GET /api/v1/admin/jobs`: 전체 작업 목록 및 요약 정보.
- `GET /api/v1/admin/jobs/{job_id}/logs`: 특정 스크래핑/인제스션 작업의 상세 실행 로그.

#### [Module 2] Storage Integrity (Page 5)
- `GET /api/v1/admin/storage/stats`: Neo4j vs Chroma 청크 개수 및 Integrity Score.
- `GET /api/v1/admin/storage/reports`: 문서별 드릴다운 리포트 (필터: `search`, `status`).
- `GET /api/v1/admin/storage/documents/{doc_id}/diagnostic`: 유실된 청크 샘플 프리뷰.
- `GET /api/v1/admin/storage/documents/{doc_id}/preview-context`: RAG 정제 컨텍스트 미리보기.
- `POST /api/v1/admin/storage/documents/{doc_id}/sync`: 단일 문서 동기화/메타데이터 보정.
- `POST /api/v1/admin/storage/documents/{doc_id}/enrich`: 지식 그래프 재추출.
- `POST /api/v1/admin/storage/sync-all`: 전체 불일치 복구 (Background Task).
- `GET /api/v1/admin/storage/sync-all/status`: 진행률 및 실시간 처리 로그 확인.

#### [Module 3] Graph Explorer (Page 1)
- `GET /api/v1/admin/graph/schema`: 노드 라벨/관계 타입 정보.
- `GET /api/v1/admin/graph/presets`: Cypher 쿼리 프리셋 목록.
- `POST /api/v1/admin/graph/query`: Cypher 실행 결과(Nodes/Edges 리스트) 반환.

#### [Module 4] Agentic RAG & Playground (Page 4)
- **Knowledge Source (Sidebar)**:
    - `GET /api/v1/admin/rag/documents/autocomplete`: 문서 제목/URL 기반 자동완성 검색 (Query param: `q`).
- **Advanced Settings & Session Control (Sidebar)**:
    - `POST /api/v1/admin/rag/sessions`: 신규 세션(Thread) 생성 (Reset Thread).
    - `DELETE /api/v1/admin/rag/sessions/{session_id}`: 현재 세션의 대화 이력 삭제 (Clear History).
    - `POST /api/v1/admin/rag/sessions/{session_id}/config`: HITL 활성화 등 세션별 설정 업데이트.
- **Query Execution**:
    - `POST /api/v1/admin/rag/sessions/{session_id}/ask`: 대화 실행 (Input: `prompt`, `filters`, `use_hitl`).

#### [Module 5] Observability & Debug (Page 2, 3)
- `GET /api/v1/admin/rag/threads`: 활성 스레드 목록 및 상태 조회.
- `GET /api/v1/admin/rag/sessions/{session_id}/trace`: 사고 과정(LangGraph Snapshot), Intent 분석, Rewriting 결과 조회.
- `POST /api/v1/admin/rag/sessions/{session_id}/resume`: HITL 승인 및 실행 재개.
- `POST /api/v1/admin/feedback`: 답변별 👍/👎 평가 저장.

### 2. Physical & Logical Isolation Requirements
- **Zero Import Rule**: `admin/` 폴더 및 **관련 테스트 코드** 내 어떤 파일에서도 `from app...` 또는 `import app...` 구문이 존재해서는 안 됨.
- **Environment Isolation**: `admin` 컨테이너는 DB URI 설정을 갖지 않으며, 오직 `API_URL` 환경변수만 참조함.
- **Test Isolation**: Admin UI 테스트는 `mock_api_client`를 사용하거나 로컬 API 서버를 띄워서 테스트해야 하며, 절대 `app.services`를 직접 호출해선 안 됨.

#### 3. API 중심 테스트 전략 (API-Centric Testing)
- **테스트 일관성**: Admin UI 기능에 대한 모든 통합/E2E 테스트는 백엔드 내부 객체(Repository, Service)를 직접 Mocking 하거나 사용하지 않고, 반드시 **실제 API 엔드포인트**를 호출하거나 API 수준에서의 Mocking을 수행하여 검증합니다.
- **Contract Verification**: 백엔드 API 명세가 변경될 경우 UI 테스트가 즉시 실패하도록 설계하여 레이어 간의 계약(Contract)을 보호합니다.

#### 4. 인프라 격리 (Docker Enforcement)
- `docker-compose.yml`에서 Streamlit 컨테이너가 DB 네트워크 또는 환경변수(DB URL)를 가지지 않도록 격리.
- 오직 Backend API 서버하고만 통신하도록 설정.

#### 2. Streamlit 코드 리팩토링 (Thin Client)
- `app/admin` 내의 직접적인 DB 접속 로직(`get_neo4j_driver`, `Neo4jStorage`, `ChromaStorage` 등)을 제거.
- `app/admin/utils/api_client.py`를 통해 모든 데이터 요청을 위 API로 대체.

#### 3. 인프라 격리
- Docker Compose 설정을 변경하여 Streamlit 컨테이너의 DB 포트 접근 차단(선택 사항).

### Non-Functional Requirements
1. **API 응답 지연 최소화**: 기존 직접 DB 접근과 비교하여 유의미한 성능 저하가 없어야 함.
2. **UI/UX 유지**: 사용자 입장에서는 기존 Admin Dashboard의 기능과 조작감이 동일하게 유지되어야 함.

## ✅ Definition of Done
1.  Streamlit 코드 내에서 `app/infrastructure` 또는 `app/domain`을 직접 import 하는 로직 제거 (일부 schema 제외).
2.  모든 Admin Dashboard 기능이 Backend API를 통해 정상 작동함을 확인.
3.  새로운 Admin API에 대한 Swagger 문서가 생성되고 정상 호출됨을 확인.
4.  테스트 스위트(`pytest`)가 전체 통과함.
