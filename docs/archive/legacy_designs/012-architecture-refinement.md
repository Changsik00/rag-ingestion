# Design Guide 011: Architecture Refinement Strategy

## 1. Overview
Spec 050에서 Clean Architecture의 기반(4-Layer, Dependency Rule)을 다졌다면, **Spec 051**은 **Consistency & Cleanliness**를 완성하는 단계입니다. 본 문서는 Spec 050 PR Review에서 식별된 "P0(기본 수정)"를 제외한 "P1~P3(고도화)" 항목들에 대한 리팩토링 가이드를 제공합니다.

---

## 2. Refactoring Scope

### ✅ P0 (Completed in Spec 050)
* **Dependency Rule Enforcement**: `checker.py` (Infrastructure → Presentation) 의존성 제거
* **Repository Pattern Naming**: `*Storage` → `*Repository` (Neo4j, Chroma, Composite)
* **LLM Interface**: `LLMInterface` Protocol과 `LLMInvoker` 분리

<br>

### 🚀 P1: High Priority (Structural Consistency)

#### 2.1 Service vs Component Naming
**원칙**: Domain Service는 행위의 주체이므로 과도한 `Service` 접미사는 제거한다. 기술적인 역할(Adapter 등)은 명확한 역할명을 부여한다.

| Current Name | New Name | Justification |
|--------------|----------|---------------|
| `IntegrityService` | `Integrity` | "무결성" 도메인 개념 그 자체 |
| `FeedbackService` | `Feedback` | "피드백" 도메인 개념 그 자체 |
| `LangChainLLMAdapter` | `LangChainExtractor` | LLM을 이용해 **추출(Extract)** 하는 구체적 구현체 |
| `LangGraphAdapter` | `LangGraphOrchestrator` | 흐름을 **제어(Orchestrate)** 하는 구체적 구현체 |

#### 2.2 Domain Object Taxonomy (Entity vs VO)
**원칙**:
* **Entity**: 식별자(ID)가 있고 수명주기(Lifecycle)가 존재하는 객체
* **Value Object (VO)**: 식별자 없이 값(Value)만으로 등가성이 증명되는 불변 객체

| Object | Type | Location Change |
|--------|------|-----------------|
| `Chunk` | **VO** | `domain/entities/` → `domain/value_objects/` |
| `ExtractedMetadata` | **VO** | `domain/value_objects/` (현행 유지) |
| `Document` | **Entity** | `domain/entities/` (현행 유지) |

#### 2.3 Interface Segregation (Chunker)
**현행**: `app/domain/services/chunker.py` (Concrete Class)
**변경**: 인터페이스(Protocol) 도입

```python
# app/domain/interfaces/chunker.py
class Chunker(Protocol):
    def chunk(self, text: str) -> list[Chunk]:
        ...
```
* **이유**: `LangChainRecursiveCiunkrt` 외에 `SemanticChunker` 등 다양한 구현체 교체 용이성 확보

#### 2.4 API Versioning & Clean Call
* **Problem**: MCP Server가 내부 구현(`RAGService`) 클래스를 직접 인스턴스화하여 사용 중.
* **Solution**: MCP Server는 외부 클라이언트처럼 취급하여, 내부 API를 호출하거나 Service Interface만 의존하도록 변경 (이번 단계에서는 Service DI 활용 권장).
* **Action**: `app/interfaces/api/v1` 구조 활성화 및 Router 정리.

---

## 3. P2: Medium Priority (Organization)

#### 3.1 Function Location (`file_processor.py`)
* `file_processor`가 상태를 가지지 않는 순수 함수들의 집합이라면 `app/shared/utils` 또는 `app/domain/utils`로 이동.

#### 3.2 AI Implementation Grouping
`infrastructure` 내부에 산재된 AI 관련 구현체들을 응집도 있게 정리.

```
app/infrastructure/ai/
├── extractors/  (LangChainExtractor)
├── orchestrators/ (LangGraphOrchestrator)
└── nodes/       (Graph Nodes Implementation)
```

---

## 4. P3: Low Priority (Nitpicks)

#### 4.1 State Definitions
* `state.py`가 여러 곳에 산재(`domain/ingestion/state.py`, `domain/rag/state.py`)
* `GraphState` 등으로 명확히 리네이밍 고려.

#### 4.2 DTO Naming
* `schemas` 디렉토리를 `dto`로 변경하여 DDD 관례 준수 (선택 사항).

---

## 5. Execution Strategy

1. **Phase 1 (Domain cleanup)**: Service Renaming, VO 이동, Chunker Protocol
2. **Phase 2 (Infrastructure cleanup)**: Adapter Renaming, AI Folder Restructuring
3. **Phase 3 (Interface cleanup)**: API v1, MCP Refactoring
