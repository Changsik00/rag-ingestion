# Spec 001: FastAPI & Web Collector Skeleton

## 1. Background
현재 프로젝트는 RAG 시스템을 위한 데이터 수집 파이프라인의 재구축 단계입니다. 이전에 시도했던 추상적인 설계를 벗어나, 실제로 동작하는 서버와 수집 기능을 최우선으로 확보하는 Vertical Slice MVP 전략을 채택했습니다.

## 2. Requirements
- **Dependency Management**: `uv`를 사용해야 합니다.
- **Web Server**: `FastAPI`로 구축해야 하며, 비동기 처리를 기본으로 합니다.
- **Endpoint**: `POST /ingest/web` 요청 시 URL을 받아 해당 페이지의 내용을 Markdown으로 반환해야 합니다.
- **Architecture**: 사용자 정의 Clean Architecture 폴더 구조를 준수해야 합니다.
    - `app/domain` (Entities & Interfaces)
    - `app/infrastructure` (Adapters: Scrapers, DB)
    - `app/use_cases` (Application Logic)
    - `app/interfaces` (Drivers: API, CLI)

## 3. Out of Scope (For this Spec)
- 데이터베이스(Neo4j, ChromaDB) 연동 (다음 Spec에서 진행)
- 동적 페이지(JS) 렌더링 처리
- 인증 및 권한 관리
- 대량 수집 및 비동기 작업 큐
