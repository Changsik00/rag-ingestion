# feat(spec-042): implement db reset arch and admin ui

## 📋 Summary

### 배경 및 목적
RAG 시스템 개발 및 테스트 과정에서 DB(Neo4j, ChromaDB, SQLite)에 정합성이 맞지 않는 데이터가 쌓이는 문제가 지속적으로 발생했습니다. 이로 인해:
- ❌ **테스트 신뢰성 저하**: 이전 테스트의 데이터 잔여물로 인해 새로운 테스트가 실패하거나 오작동
- ❌ **운영 비효율**: 데이터를 초기화하기 위해 각 DB에 수동으로 접속하거나 스크립트를 실행해야 함
- ❌ **UI 경험 저하**: Streamlit 새로고침 시 대화 이력이 날아가 디버깅이 어려움

이를 해결하기 위해 **통합 데이터 초기화(Integrity Reset)** 아키텍처와 **UI 세션 유지(Persistence)** 기능을 구현했습니다:

### Before (파편화된 관리)
- **Reset**: `MATCH (n) DETACH DELETE n` (Neo4j 브라우저), `rm checkpoints.sqlite` (터미널) 등 수동 수행
- **Persistence**: Streamlit 새로고침 = 대화 초기화 (Thread ID 유실)

### After (통합 관리 및 UI 제공)
```python
# 1. IntegrityService: 3개 저장소 동시 초기화
class IntegrityService:
    async def reset_all(self):
        self.neo4j.reset_database()       # Node/Relationship 삭제
        self.chroma.reset_collection()    # Collection 재생성
        await self.adapter.reset_checkpoints() # SQLite Tables Truncate

# 2. Admin UI Integration
# "Danger Zone" 버튼 클릭 시 API 호출로 원클릭 초기화
```
- **Reset**: Admin UI "Danger Zone"에서 버튼 하나로 모든 DB 초기화
- **Persistence**: URL Query Param(`?thread_id=...`)을 통해 새로고침 후에도 대화 세션 복원

### 주요 변경 사항
1. **Infrastructure Layer 확장**
   - `Neo4jStorage`, `ChromaStorage`: `reset_*` 메서드 구현
   - `LangGraphAdapter`: SQLite `reset_checkpoints` 구현 (aiosqlite 활용)

2. **Application Layer 신규**
   - `IntegrityService`: 여러 저장소의 초기화 로직을 관장하는 Facade 서비스 구현

3. **Admin API 신규**
   - `POST /api/v1/admin/integrity/reset`: 시스템 완전 초기화 엔드포인트

4. **Streamlit UI 개선 (RAG Playground)**
   - **Danger Zone**: 시스템 초기화 UI 추가
   - **Session Persistence**: `st.query_params` 및 Backend Trace API 연동

## 🎯 Key Review Points

1. **Destructive Operation Safety**: 
   - `reset_all`은 복구 불가능한 작업이므로 Admin API로만 노출되며, 실제 운영 환경에서는 접근 제어가 필요합니다. (현재는 로컬/개발용)
   
2. **Persistence Logic**: 
   - Streamlit의 `st.query_params`를 사용하여 `thread_id`를 URL에 고정하고, `Page Refresh` 시 백엔드 `/trace` API를 통해 `messages` 상태를 복원하는 흐름입니다.

3. **Dependency Injection**: 
   - `get_integrity_service`를 통해 필요한 모든 저장소 인스턴스(Neo4j, Chroma, Adapter)를 주입받도록 구성했습니다.

## 🧪 Verification

### Automated Tests
```bash
# Integration Tests (Reset API 전체 흐름 검증)
uv run pytest tests/integration/test_integrity_api.py -v
# ✅ 결과: Passed
```
**테스트 커버리지:**
- ✅ `IntegrityService`가 Neo4j, Chroma, SQLite 리셋 메서드를 모두 호출하는지 검증
- ✅ API 엔드포인트 정상 응답(200 OK) 확인

### Manual Verification (Admin Dashboard 시나리오)

#### 📝 시나리오 1: 시스템 초기화 (Danger Zone)
**Given**: Neo4j와 ChromaDB에 문서 데이터가 존재하고, 채팅 이력이 쌓인 상태
**When**: RAG Playground Sidebar -> "Danger Zone" -> "💣 RESET ALL SYSTEM DATA" 클릭
**Then**:
1. "System Reset Successful!" 메시지 표시
2. Neo4j Browser에서 `MATCH (n) RETURN count(n)` 조회 시 0 확인
3. SQLite 파일(`checkpoints.sqlite`) 사이즈 초기화 확인

#### 📝 시나리오 2: 세션 유지 (Persistence)
**Given**: RAG Playground에서 "인공지능이란?" 질문 후 답변을 받은 상태
**When**: 브라우저 새로고침 (F5) 수행
**Then**:
1. 대화 내용이 사라지지 않고 유지됨
2. URL에 `?thread_id=playground-xxxx` 파라미터 유지 확인
3. "Restored X messages from history" 토스트 메시지 표시

## 📦 Files Changed

### 🆕 New Files (3개)
- `app/application/admin/integrity_service.py`: 초기화 비즈니스 로직
- `app/interfaces/api/v1/endpoints/admin/integrity.py`: 초기화 API 엔드포인트
- `tests/integration/test_integrity_api.py`: 통합 테스트

### 🛠 Modified Files (5개)
- `app/infrastructure/storage/neo4j_document_repository.py`: `reset_database` 추가
- `app/infrastructure/storage/chroma.py`: `reset_collection` 추가
- `app/infrastructure/brain/adapter.py`: `reset_checkpoints` 추가
- `app/interfaces/api/dependencies.py`: DI 추가
- `admin/pages/4_RAG_Playground.py`: Danger Zone 및 Persistence 로직 추가

**Total:** 8 files changed

## ✅ Definition of Done
- [x] Infrastructure Reset 메서드 구현 (Neo4j, Chroma, SQLite)
- [x] IntegrityService 및 Admin API 구현
- [x] Admin UI "Danger Zone" 추가
- [x] Admin UI Session Persistence 구현
- [x] Integration Test 작성 및 통과
- [x] Code Quality Check (Ruff)
