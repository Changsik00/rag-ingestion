# PR Description: Spec-049 Local File Ingestion (PDF, TXT, MD)

## 📋 개요 (Summary)
RAG 시스템의 데이터 소스 유연성을 높이기 위해 로컬 파일(PDF, TXT, MD)을 직접 업로드하고 인제스션할 수 있는 기능을 구현하였습니다. 대용량 파일 처리를 위한 'Divide and Conquer' 전략이 적용되었습니다.

## 🚀 주요 변경 사항 (Main Changes)

### 1. Backend (Domain & UseCase)
- **FileProcessor**: `PyMuPDF`를 활용한 제너레이터 기반의 세그먼트 추출 로직 구현. 페이지 단위로 데이터를 스트리밍하여 메모리 효율성 확보.
- **IngestionService**: 파일의 각 세그먼트별로 Semantic Extraction 및 Graph Indexing을 반복 수행하는 반복적 파이프라인(Iterative Pipeline) 구축.
- **Entity**: `IngestionJob`에 `docs_ids` 추가로 분할 저장된 문서 추적 기능 강화.

### 2. API Layer
- **Multipart API**: `POST /ingest/file` 엔드포인트 추가로 바이너리 데이터 수집 지원.

### 3. Frontend (Admin Dashboard)
- **Ingestion Management**: URL과 파일을 구분하여 수집할 수 있는 전용 페이지 신설.
- **RAG Playground**: 사이드바에 'Quick File Upload' 위젯 추가로 채팅 도중 실시간 지식 주입 가능.

## 🧪 검증 내용 (Verification)
- **Unit Tests**: `tests/unit/test_file_processor.py`를 통해 다양한 포맷의 파싱 및 세그먼트 분할 검증 완료.
- **Manual Test**: `scripts/verify_file_ingestion.py`를 사용하여 API 엔드포인트와 비동기 처리 흐름 확인.

## 📸 스크린샷 (예시)
- `Admin > Ingestion Management`: 신규 수집 탭
- `Admin > RAG Playground`: 사이드바 업로드 위젯

---
**관련 문서**: [Walkthrough](specs/049-local-file-ingestion/walkthrough.md), [Spec](specs/049-local-file-ingestion/spec.md)
