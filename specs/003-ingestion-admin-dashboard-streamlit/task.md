# Spec 003 Tasks

## Backend Implementation
- [ ] Domain Layer
  - [ ] `IngestionJob` Entity & `JobStatus` Enum 정의 <!-- id: 0 -->
  - [ ] `JobRepository` Interface 정의 <!-- id: 1 -->
- [ ] Infrastructure Layer
  - [ ] `Neo4jJobRepository` 구현 (Save, FindAll, FindById) <!-- id: 2 -->
- [ ] Application Layer
  - [ ] `IngestionService` 수정: 작업 시작/종료 시 Job 상태 업데이트 로직 추가 <!-- id: 3 -->
  - [ ] `RetryJobService` (Optional) or `IngestionService`에 재시도 로직 추가 <!-- id: 4 -->
- [ ] Interface Layer (API)
  - [ ] `GET /jobs` 엔드포인트 구현 <!-- id: 5 -->
  - [ ] `GET /jobs/{job_id}` 엔드포인트 구현 <!-- id: 6 -->
  - [ ] `POST /jobs/{job_id}/retry` 엔드포인트 구현 <!-- id: 7 -->
  - [ ] `main.py` 라우터 등록 및 의존성 주입 <!-- id: 8 -->

## Frontend Implementation (Streamlit)
- [ ] `app/admin` 디렉토리 생성 및 `dashboard.py` 초기화 <!-- id: 9 -->
- [ ] `docker-compose.yml`에 Streamlit 서비스 추가 <!-- id: 10 -->
- [ ] UI 구현
  - [ ] API Client 함수 구현 (requests 사용) <!-- id: 11 -->
  - [ ] Sidebar 및 Main Layout 구성 <!-- id: 12 -->
  - [ ] Job List Table 구현 (st.dataframe or st.table) <!-- id: 13 -->
  - [ ] Job Detail View 구현 (Log Expander) <!-- id: 14 -->
  - [ ] Retry Button Action 구현 <!-- id: 15 -->

## Documentation & Verification
- [ ] `docs/admin_guide.md` 작성 (대시보드 사용법) <!-- id: 16 -->
- [ ] 통합 테스트 (API + DB) <!-- id: 17 -->
- [ ] 수동 테스트 (UI 동작 확인) <!-- id: 18 -->
