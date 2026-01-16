# Spec 003: Ingestion Admin Dashboard (Streamlit)

## Goal
현재 수집 시스템의 가시성을 확보하기 위해 **Streamlit**을 이용한 Admin Dashboard를 구축합니다.
수집 작업(Job)의 이력을 추적하고, 실패한 작업에 대해 원인을 파악하며 재시도(Retry)할 수 있는 기능을 제공합니다.

## Background
현재 시스템은 API(`POST /ingest/web`)를 통해 수집을 요청하면 즉시 처리되지만, 그 과정과 결과 히스토리를 체계적으로 조회할 수 있는 UI가 부재합니다.
운영 관점에서 "무엇이 수집되었고, 무엇이 실패했는가"를 한눈에 파악할 수 있어야 하며, 실패 건에 대한 대응책이 필요합니다.

## Requirements

### 1. Job Tracking (Backend Support)
- **IngestionJob Entity**: 수집 요청 건별로 고유한 Job을 생성하여 상태를 관리해야 합니다.
  - Fields: `job_id`, `source_url`, `status` (PENDING, RUNNING, COMPLETED, FAILED), `created_at`, `updated_at`, `error_message`
- **Persistence**: Job 데이터를 Neo4j에 저장합니다.
- **Service Logic Update**: `IngestionService` 실행 시 Job 생성 및 상태 업데이트 로직을 주입합니다.

### 2. API Layer
- `GET /jobs`: 전체 작업 목록 조회 (페이징 지원 또는 최근 50건)
- `GET /jobs/{job_id}`: 작업 상세 조회 (로그/에러 메시지 포함)
- `POST /jobs/{job_id}/retry`: 실패한 작업 재실행 요청

### 3. Streamlit Dashboard (UI)
- **URL**: `http://localhost:8501` (별도 포트)
- **Features**:
  - **Job List**: 최근 작업 목록을 테이블 형태로 표시 (상태별 색상 구분).
  - **Status Filter**: 성공/실패/진행중 필터링.
  - **Detail View**: 리스트 항목 클릭 시 상세 정보(메타데이터, 에러 로그) 표시.
  - **Retry Action**: 실패한 항목에 대해 '재시도' 버튼 제공 (백엔드 API 호출).

## Constraints
- Streamlit 앱은 `app/admin` 디렉토리 내에 위치시킵니다.
- 기존 `fastapi` 서버와는 별도 프로세스로 실행되지만, `docker-compose`에 포함하여 관리합니다.
