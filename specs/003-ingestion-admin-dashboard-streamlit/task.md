# Spec 003 Tasks

## Backend Implementation (백엔드 구현)
- [ ] Domain Layer 구성
  - [ ] `IngestionJob` Entity & `JobStatus` Enum 정의 <!-- id: 0 -->
  - [ ] `JobRepository` Interface 정의 <!-- id: 1 -->
- [ ] Infrastructure Layer 구성
  - [ ] `Neo4jJobRepository` 구현 (Save, FindAll, FindById) <!-- id: 2 -->
- [ ] Application Layer 수정
  - [ ] `IngestionService` 수정: 작업 시작/종료 시 Job 상태 업데이트 로직 추가 <!-- id: 3 -->
- [ ] Interface Layer (API) 구현
  - [ ] `GET /jobs` 엔드포인트 구현 <!-- id: 5 -->
  - [ ] `GET /jobs/{job_id}` 엔드포인트 구현 <!-- id: 6 -->
  - [ ] `POST /jobs/{job_id}/retry` 엔드포인트 구현 <!-- id: 7 -->
  - [ ] `main.py` 라우터 등록 및 의존성 주입 <!-- id: 8 -->

## Frontend Implementation (Streamlit 구현)
- [ ] `app/admin` 디렉토리 생성 및 `dashboard.py` 초기화 <!-- id: 9 -->
- [ ] `docker-compose.yml`에 Streamlit 서비스 추가 <!-- id: 10 -->
- [ ] UI 기능 구현
  - [ ] API Client 함수 구현 (requests 사용) <!-- id: 11 -->
  - [ ] 사이드바(Sidebar) 및 메인 레이아웃 구성 <!-- id: 12 -->
  - [ ] 작업 목록(Job List) 테이블 구현 <!-- id: 13 -->
  - [ ] 작업 상세(Detail) 및 로그 뷰어 구현 <!-- id: 14 -->
  - [ ] 재시도(Retry) 버튼 액션 구현 <!-- id: 15 -->

## Documentation & Verification (문서화 및 검증)
- [ ] `docs/admin_guide.md` 작성 (대시보드 사용 가이드) <!-- id: 16 -->
- [ ] 통합 테스트 수행 (API + DB) <!-- id: 17 -->
- [ ] 수동 테스트 수행 (UI 동작 확인) <!-- id: 18 -->
