## 🔍 What is this PR?
**Title**: feat(spec-065): Semantic De-Duplication Logic & Strategy

**Spec**: [Spec 065: Semantic De-Duplication](specs/065-semantic-deduplication/spec.md)

**Description**:
이 PR은 중복 데이터 수집을 방지하기 위한 중복 제거 로직을 도입합니다. 단순한 URL 비교를 넘어, 메타데이터(Metadata)와 콘텐츠 해시(Content Hash)를 기반으로 중복을 판단하는 유연한 전략 패턴을 구현했습니다.

## ✨ Key Changes
*   **Infrastructure**: `IngestionJob` 모델에 `content_hash`, `custom_metadata` 필드 추가. `Neo4jJobRepository` 업데이트.
*   **Domain Service**: 
    *   `DeduplicationStrategy` (Abstract Base Class)
    *   `MetadataComparisonStrategy`: `video_id`, `file_size` 등 메타데이터 Key 비교.
    *   `ContentHashStrategy`: 콘텐츠 해시값 비교.
    *   `DeduplicationFactory`: Source Type에 맞는 전략 제공.
*   **Application**: `Ingestion` 서비스에 Deduplication Check 통합. 중복 시 `SKIPPED` 처리.
*   **Interface**: API 및 Admin UI에 `force_refresh` 옵션 추가.

## 🧪 Testing
- [x] Unit Test: `tests/unit/test_deduplication_strategies.py` (Passed)
- [x] Integration Test: `tests/integration/test_ingestion_deduplication.py` (Passed)
- [x] Manual Verification: Admin UI Checkbox logic verified via code review.

## 📸 Screenshots
(UI 변경 사항 스크린샷은 생략 - Checkbox 추가됨)
