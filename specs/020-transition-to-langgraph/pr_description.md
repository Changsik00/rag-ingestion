feat(spec-020): transition to langgraph for ingestion pipeline

## 📋 Summary
기존 LangChain `RunnableSequence` 기반의 선형 수집 파이프라인을 **LangGraph `StateGraph`** 기반의 상태 머신 아키텍처로 전환했습니다. 이는 Phase 4에서 계획된 **순환(Cycle)**, **조건부 분기(Conditional Logic)**, **Human-in-the-loop** 워크플로우를 지원하기 위한 필수적인 기반 작업입니다.

> **Decision Record**: [ADR 001: From Linear DAG to Stateful Graph](docs/architecture_decisions/001_dag_to_graph_transition.md)

## 🔍 Key Review Points
- **Architecture**: `app/infrastructure/brain/graph.py`의 그래프 구성이 적절한가?
- **State Management**: `IngestionState` (TypedDict)의 필드 구조가 적절한가?
- **Compatibility**: 기존 `IngestionService`가 `LangGraphAdapter`를 통해 문제없이 작동하는가? (`test_success_flows.py` 통과)
- **Migration**: 기존 동기식 `LLMInterface`를 지원하기 위해 Node들을 동기 함수(`def`)로 구현한 전략.

## 🧪 Verification
- **Unit Tests**: Graph Builder, Nodes, State 검증 (New) 
- **Integration Tests**: `test_langgraph_adapter.py` (New), `test_success_flows.py` (Regression Pass)
- **Deployment**: n/a (내부 로직 변경)

## 📌 References
- Spec 020
- ADR 001
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
