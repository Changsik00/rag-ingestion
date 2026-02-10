from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.application.services.orchestration.chat import ChatOrchestrator
from app.domain.value_objects.rag_state import RAGGraphState


class ChatGraphBuilder:
    """
    Builds the Chat Graph using the ChatOrchestrator.
    Maps graph nodes to orchestrator methods for granular visibility and control.
    """

    def __init__(self, orchestrator: ChatOrchestrator):
        self.orchestrator = orchestrator

    def build(self, checkpointer: Any = None, interrupt_before: list[str] | None = None) -> CompiledStateGraph:
        workflow = StateGraph(RAGGraphState)

        # === Node Definitions (Adapters) ===

        async def classify_adapter(state: RAGGraphState, config: RunnableConfig):
            # 1. Classify
            intent, rewritten = await self.orchestrator.classify(state["query"], state.get("history", []))
            return {"user_intent": intent, "rewritten_query": rewritten}

        async def route_adapter(state: RAGGraphState, config: RunnableConfig):
            # 2. Route
            filters = await self.orchestrator.route_filters(state.get("user_intent"), state.get("manual_filters"))
            return {"final_filters": filters}

        async def search_adapter(state: RAGGraphState, config: RunnableConfig):
            # 3. Search
            logs = []
            final_filters = state.get("final_filters", {})
            user_intent = state.get("user_intent")

            vector, keyword, graph, fallback = await self.orchestrator.search(
                state.get("rewritten_query"), final_filters, user_intent, config, logs
            )

            # Append logs manually because state reducer is 'replace' (lambda x,y: y)
            current_logs = state.get("reasoning_log", [])
            new_logs = current_logs + logs

            return {
                "vector_chunks": vector,
                "keyword_chunks": keyword,
                "graph_data": graph,
                "fallback_triggered": fallback,
                "reasoning_log": new_logs,
            }

        async def rerank_adapter(state: RAGGraphState, config: RunnableConfig):
            # 4. Rerank
            logs = []
            vector = state.get("vector_chunks", [])
            keyword = state.get("keyword_chunks", [])

            reranked, rerank_log = await self.orchestrator.rerank(
                state.get("rewritten_query"), vector, keyword, config, logs
            )

            current_logs = state.get("reasoning_log", [])
            new_logs = current_logs + logs

            return {"reranked_chunks": reranked, "rerank_log": rerank_log, "reasoning_log": new_logs}

        async def generate_adapter(state: RAGGraphState, config: RunnableConfig):
            # 5. Generate
            answer, citations, context = await self.orchestrator.generate(
                state["query"],
                state.get("rewritten_query"),
                state.get("vector_chunks", []),
                state.get("keyword_chunks", []),
                state.get("graph_data", []),
                state.get("reranked_chunks", []),
                config,
            )
            return {"final_answer": answer, "citations": citations, "full_context": context}

        # === Add Nodes ===
        workflow.add_node("classify", classify_adapter)
        workflow.add_node("route", route_adapter)
        workflow.add_node("search", search_adapter)
        workflow.add_node("rerank", rerank_adapter)
        workflow.add_node("generate", generate_adapter)

        # === Define Edges ===
        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "route")
        workflow.add_edge("route", "search")
        workflow.add_edge("search", "rerank")
        workflow.add_edge("rerank", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)
