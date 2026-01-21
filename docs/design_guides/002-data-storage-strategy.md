# Design Guide 002: Data Storage Strategy (JSONL vs SQLite vs Postgres)

## 1. 개요 (Overview)
본 시스템은 목적에 따라 서로 다른 데이터 저장소 전략을 사용합니다.
초기 단계(Phase 2-3)에서는 **개발 속도(Agility)**와 **목적 적합성(Fitness for Purpose)**을 최우선으로 하여, 단일 데이터베이스(Monolithic DB) 대신 파일 기반의 경량 저장소(SQLite, JSONL)를 혼용하는 전략을 채택했습니다.

## 2. 저장소별 전략 및 근거 (Strategy & Rationale)

### 2.1 Interaction Feedback (`feedback.jsonl`)
사용자가 RAG 답변에 대해 제공하는 피드백(👍/👎)을 저장합니다.

*   **저장 방식**: `Append-only JSON Lines` (텍스트 파일)
*   **선택 근거**:
    1.  **AI 학습 표준 (Training Standard)**: OpenAI, Google Cloud Vertex AI 등 대부분의 Fine-tuning API는 데이터셋 포맷으로 JSONL을 요구합니다. DB에 저장했다가 다시 JSONL로 변환하는 오버헤드를 제거했습니다.
    2.  **쓰기 성능 (Write Performance)**: 단순 Append 작업은 DB 트랜잭션보다 빠르고 부하가 적습니다.
    3.  **유연성 (Schema Flexibility)**: 피드백 데이터는 구조가 자주 바뀔 수 있습니다(Metadata 추가 등). NoSQL 특성이 필요합니다.

### 2.2 LangGraph State Checkpoints (`checkpoints.sqlite`)
에이전트의 실행 상태(State Snapshot)를 저장하여 `Interrupt`(일시정지) 및 `Resume`(재개) 기능을 지원합니다.

*   **저장 방식**: `SQLite` (바이너리 객체 저장)
*   **선택 근거**:
    1.  **임의 접근 (Random Access)**: 특정 스레드의 최신 상태나 과거 상태를 빠르게 조회해야 합니다. (로그 파일 불가)
    2.  **무결성 (Integrity)**: 바이너리(Pickle) 데이터를 안전하게 저장하기 위해 BLOB 타입 지원이 필요합니다.
    3.  **동시성 제어 (Concurrency)**: 여러 스레드가 동시에 상태를 갱신할 때 락(Lock) 메커니즘이 필요합니다.

### 2.3 Knowledge Graph & Vectors (`Neo4j`, `ChromaDB`)
RAG의 핵심 지식 저장소입니다.

*   **Neo4j**: 관계형 데이터 및 그래프 탐색용.
*   **ChromaDB**: 시맨틱 검색을 위한 벡터 임베딩 저장용. (현재 Docker 컨테이너 내에서 실행)

## 3. 향후 마이그레이션 계획 (Migration Plan)

시스템이 확장됨에 따라 파일 기반 저장소의 한계(확장성, 백업 등)가 발생할 수 있습니다.
**Phase 4+** 단계에서는 다음과 같이 통합을 고려합니다.

### 3.1 Unified Database (PostgreSQL)
*   **대상**: `checkpoints.sqlite` + `feedback.jsonl`
*   **전략**:
    *   `PostgresSaver` (LangGraph) 도입으로 체크포인트를 Postgres로 이관.
    *   `JSONB` 컬럼을 활용하여 Feedback 데이터를 Postgres에 저장.
*   **장점**: 중앙화된 백업, 강력한 쿼리 및 분석 기능, 수평적 확장 용이성.

### 3.2 Data Lake / Warehouse
*   **대상**: 대량의 `feedback.jsonl`
*   **전략**: S3/GCS 등으로 피드백 로그를 주기적으로 아카이빙하고, BigQuery/Snowflake와 연동하여 분석 수행.

## 4. 관련 백로그
*   **Spec 022 (Completed)**: HITL Checkpointer (SQLite)
*   **Icebox - HITL Persistence**: PostgresSaver 도입 계획
