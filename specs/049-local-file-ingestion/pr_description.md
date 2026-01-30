# feat(spec-049): multi-file upload & drag-and-drop support

## 📋 Summary

### 배경 및 목적
기존의 단일 파일 업로드 방식을 확장하여, 사용자가 여러 문서(PDF, TXT, MD)를 동시에 선택하거나 폴더째로 드래그 앤 드롭하여 대량의 지식을 한 번에 수집할 수 있도록 사용성을 개선하였습니다.

### 주요 변경 사항
- [x] **Multi-File API**: `POST /ingest/files` 엔드포인트를 구현하여 리스트 형태의 `UploadFile`을 한 번에 처리하고 개별 `job_id`를 반환하도록 고도화.
- [x] **Drag-and-Drop UI**: Streamlit의 `st.file_uploader`에 `accept_multiple_files=True`를 적용하여 직관적인 다중 선택 및 드래그 앤 드롭 지원.
- [x] **Batch Processing**: 업로드된 모든 파일에 대해 개별 인제스션 작업을 비동기적으로 생성하여 병렬 처리 및 진행 추적 가능.

## 🎯 Key Review Points
1. **Memory Efficiency**: `FileProcessor.extract_segments`가 제너레이터로서 파일을 한 번에 메모리에 올리지 않고 스트리밍 처리하는지 확인.
2. **Data Consistency**: 세그먼트별로 루프를 돌 때 메타데이터(`page_number` 등)가 정확히 각 `Document`와 `Knowledge Graph`에 전달되는지 확인.
3. **UI/UX**: 관리자 대시보드에서 파일 업로드 시 `Job Queue`를 통해 실시간 상태 확인이 가능한지 여부.

## 🧪 Verification

### Automated Tests
```bash
# FileProcessor 단위 및 세그먼트 분할 테스트
uv run pytest tests/unit/test_file_processor.py
```
**테스트 결과 요약:**
- ✅ `test_pdf_segmentation`: 대형 PDF 페이지별 분할 성공
- ✅ `test_text_encoding`: UTF-8/CP949 자동 감지 및 파싱 성공

### Manual Verification (Scenarios)
1. **시나리오 1: 관리자 대시보드 통합 수집**
   - `Admin > Ingestion Management` 페이지 접속
   - `Local File Ingestion` 탭에서 샘플 PDF(예: 10페이지 이상) 업로드
   - `🚀 Upload & Ingest` 클릭 후 상단에 생성된 `Job ID` 확인
   - `Job Queue` 페이지로 이동하여 해당 작업이 `COMPLETED`로 변하고, 'Source' 열에 `file://...` 경로가 표시되는지 확인

2. **시나리오 2: 플레이그라운드 퀵 업로드 및 대화**
   - `Admin > RAG Playground` 접속
   - 사이드바의 `📁 Quick File Upload` 위젯에 TXT 또는 MD 파일 업로드
   - 업로드 완료 메시지(`✅ 파일 수집 완료`) 확인 후 채팅창에 파일 내용과 관련된 질문 수행
   - 생성된 답변 하단의 `📚 References`에 해당 파일명이 출처로 정상 표시되는지 확인

3. **시나리오 3: 대용량 처리 검증 (Script)**
   - 터미널에서 `uv run python scripts/verify_file_ingestion.py` 실행
   - 임시 테스트 파일 생성 -> 업로드 API 호출 -> 비동기 상태 폴링 -> 완료 과정이 자동으로 통과하는지 확인

## 📦 Files Changed

### 🆕 New Files
- `app/domain/services/file_processor.py`: 분할 추출 엔진
- `admin/pages/0_Ingestion_Management.py`: 신규 수집 관리 UI
- `scripts/verify_file_ingestion.py`: 검증 자동화 스크립트

### � Modified Files
- `app/domain/entities/job.py`: `docs_ids` 필드 추가
- `app/use_cases/ingestion.py`: 반복적 인제스션 파이프라인 연동
- `app/interfaces/api/main.py`: 멀티파트 업로드 엔드포인트 추가
- `admin/utils/api_client.py`: 파일 업로드 `httpx` 지원 추가
- `admin/pages/4_RAG_Playground.py`: 사이드바 위젯 추가
- `admin/pages/0_Job_Queue.py`: 파일 경로 표현 개선

## ✅ Definition of Done
- [x] 모든 단위 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 완료
- [x] Ruff lint 및 format 확인 완료 (Check/Format 수행됨)
