# Implementation Plan: Spec-038 (Structural Decoupling)

## 📋 Branch Strategy
- `feature/038-structural-decoupling`

## 🛑 User Review Required
- **물리적 디렉토리 이동**: `app/admin` -> `admin/` 이동에 따라 Docker 및 CI/CD 설정을 대폭 수정해야 함.
- **의존성 차단 정책**: `admin/` 폴더 내에서 `app/` 패키지 참조 발견 시 빌드 실패 처리를 도입할지 여부.

## 🎯 Core Strategy
- **Isolation by Default**: `admin/` 디렉토리를 루트로 분리하고 DB 접근 정보를 제거하여, API 호출 없이는 어떠한 데이터도 가져올 수 없는 구조를 강제함.
- **Thin Client Architecture**: Streamlit은 오직 `httpx`를 통한 결과 렌더링에만 집중하며, 복잡한 비즈니스 상태(대화 이력, 정합성 리포트 가공)는 백엔드 Facade API가 책임짐.
- **API Centric Testing**: 모든 통합 테스트는 백엔드 도메인 객체를 직접 생성하지 않고 실제 API 엔드포인트 호출을 통해 검증함.

## 📂 Proposed Changes

### [Backend: Admin API Layer]

#### [NEW] `app/interfaces/api/v1/endpoints/admin/storage.py` (Module 2)
- `GET /stats`: 전체 정합성 지표 반환.
- `GET /reports`: 문서별 상태 리포트 (필터링 포함).
- `GET /documents/{doc_id}/diagnostic`: 샘플 데이터 확인.
- `GET /documents/{doc_id}/preview-context`: RAG용 컨텍스트 미리보기.
- `POST /documents/{doc_id}/sync`: 단일 문서 동기화.
- `POST /documents/{doc_id}/enrich`: 지식 그래프 보강.
- `POST /sync-all`: BackgroundTasks를 이용한 일괄 동기화 실행.
- `GET /sync-all/status`: 일괄 작업 상태 및 진행률 조회.

#### [NEW] `app/interfaces/api/v1/endpoints/admin/rag.py` (Module 4, 5)
- `GET /documents/autocomplete`: 문서 제목/URL 기반 검색 (Sidebar용).
- `POST /sessions`: 신규 대화 세션 생성.
- `DELETE /sessions/{session_id}`: 대화 이력 초기화.
- `POST /sessions/{session_id}/config`: 세션 설정(HITL 여부 등) 업데이트.
- `POST /sessions/{session_id}/ask`: 질문 처리 (LangGraph 실행).
- `POST /sessions/{session_id}/resume`: HITL 중단점 재개.
- `GET /sessions/{session_id}/trace`: 실행 트레이스 및 디버그 정보 조회.
- `GET /threads`: 전체 활성 스레드 목록 조회.

#### [NEW] `app/interfaces/api/v1/endpoints/admin/jobs.py` (Module 1)
- `GET /jobs`: 작업 목록 조회.
- `GET /jobs/{job_id}/logs`: 작업 로그 조회.

#### [NEW] `app/interfaces/api/v1/endpoints/admin/graph.py` (Module 3)
- `GET /schema`: 그래프 스키마 정보.
- `GET /presets`: 쿼리 프리셋.
- `POST /query`: Cypher 쿼리 실행 및 Agraph 포맷 변환.

#### [MODIFY] `app/main.py`
- 패키지화된 `admin_router`를 `/api/v1/admin`에 등록하여 관리 포인트 통합.

### [Frontend: Admin Dashboard (Thin Client)]

#### [MOVE] `app/admin` -> `admin/`
- 물리적 의존성 제거를 위해 루트 디렉토리로 이동.

#### [NEW] `admin/utils/api_client.py`
- 중앙 집중식 httpx 클라이언트. 공통 에러 처리 및 세션 관리를 담당.

#### [MODIFY] `admin/pages/*.py`
- 모든 `from app...` import를 제거하고 `api_client` 호출로 대체.
- 예시: `StorageIntegrityService.get_drift_report()` -> `api_client.get("/admin/storage/reports")`

## 🧪 Verification Plan

### Automated Tests
```bash
# Backend Admin API 통합 테스트
uv run pytest tests/integration/api/admin/

# Import 의존성 위반 체크 (검색 결과가 없어야 성공)
grep -r "from app." admin/ | grep -v "app.admin"
```

### Manual Verification
1. **Scenario 1 (Storage Recovery)**:
   - `5_Storage_Management.py` 접속 -> 진단 탭 확인 -> `sync` 버튼 클릭 -> 로컬 DB가 아닌 API를 통한 동기화 성공 확인.
2. **Scenario 2 (RAG & HITL)**:
   - `4_RAG_Playground.py`에서 HITL 켜고 질문 -> 'Paused' 상태 UI 확인 -> 'Confirm' 클릭 시 실행 재개 확인.
3. **Scenario 3 (Infrastructure Isolation)**:
   - `docker-compose` 빌드 시 `admin` 서비스에 `NEO4J_URI` 등이 없음을 확인하고 모든 기능 작동 확인.
