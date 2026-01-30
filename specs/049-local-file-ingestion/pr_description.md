# feat(spec-049): local file ingestion (pdf, txt, md) support

## 📋 Summary

### 배경 및 목적
현재 웹 크롤링에 국한된 수집 소스를 로컬 파일(PDF, TXT, MD)로 확장하여, 사용자가 보유한 개인/기업 내부 문서를 지식 베이스에 직접 통합할 수 있도록 하기 위함입니다. 특히 대용량 파일 처리 시의 부하를 방지하기 위해 '분할 정복(Iterative Segmentation)' 전략을 적용하였습니다.

### 주요 변경 사항
- [x] **Iterative File Processor**: `fitz(PyMuPDF)`를 활용하여 PDF를 페이지 단위로, TXT를 세그먼트로 분할 추출하는 제너레이터 구현.
- [x] **Ingestion Pipeline**: 세그먼트별로 순회하며 Semantic Extraction 및 인덱싱을 수행하도록 `IngestionService` 고도화.
- [x] **Job Tracking**: 단일 파일에서 생성된 여러 문서를 추적하기 위해 `IngestionJob`에 `docs_ids` 리스트 필드 추가.
- [x] **New Admin UI**: `Ingestion Management` 페이지 신설 및 `RAG Playground` 사이드바 퀵 업로드 위젯 추가.

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
