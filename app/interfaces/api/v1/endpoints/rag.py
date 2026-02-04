from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.agent import ConversationalRAGAgent
from app.application.services.feedback import Feedback
from app.domain.interfaces.document_repository import DocumentRepository
from app.interfaces.api.dependencies import (
    get_checkpointer,
    get_conversational_rag_agent,
    get_feedback_service,
    get_repository,
)
from app.interfaces.api.v1.dto.common import BaseResponse
from app.interfaces.api.v1.dto.jobs import ThreadResponse
from app.interfaces.api.v1.dto.rag import (
    AutocompleteResponse,
    ChatRequest,
    ChatResponse,
    MessageDTO,
    SessionTraceResponse,
)

router = APIRouter(tags=["RAG"])


@router.get("/documents/autocomplete", response_model=list[AutocompleteResponse])
async def autocomplete_documents(
    q: str = Query(..., min_length=1), repository: Annotated[DocumentRepository, Depends(get_repository)] = None
):
    """검색어 기반 문서 제목 자동완성"""
    docs = repository.list_documents(limit=10, search_term=q)
    return [AutocompleteResponse(id=str(d.id), title=d.metadata.title or "Untitled") for d in docs]


def map_to_chat_response(result: dict, status: str, next_steps: Any) -> ChatResponse:
    output_messages = []
    # result['messages'] might be AIMessage objects or dicts (ainvoke returns dict? output checks msg.type)
    # The original code: result.get("messages", []) -> msg.type, msg.content
    # LangGraph returns objects in "messages" usually.
    # We should handle objects.
    for msg in result.get("messages", []):
        role = getattr(msg, "type", "assistant")
        if role == "human":
            role = "user"
        if role in ["ai", "assistant"]:
            role = "assistant"
        content = getattr(msg, "content", str(msg))
        output_messages.append(MessageDTO(role=role, content=content))

    return ChatResponse(
        current_status=status,
        messages=output_messages,
        context_data=result.get("context_data"),
        intent=result.get("intent"),
        next=list(next_steps) if next_steps else None,
        draft_content=result.get("draft_content"),
        is_clarification=result.get("is_clarification", False),
        missing_slots=result.get("missing_slots"),
    )


@router.post("/sessions/{id}/ask", response_model=ChatResponse, status_code=status.HTTP_202_ACCEPTED)
async def ask_agent(
    id: str,
    payload: ChatRequest,
    agent: Annotated[ConversationalRAGAgent, Depends(get_conversational_rag_agent)],
    checkpointer=Depends(get_checkpointer),
):
    """Conversational RAG Agent에게 질문을 던지고 결과를 반환 (HITL 지원 가능)"""
    message = payload.message
    filters = payload.filters
    hitl_enabled = payload.hitl_enabled

    # Spec 055: Advanced Settings Extraction
    retrieval_config = payload.advanced_settings.model_dump()

    # LangGraph Workflow 실행
    # Spec 055: Inject retrieval_config into configurable
    config = {"configurable": {"thread_id": id, "retrieval_config": retrieval_config}}
    workflow = agent.build_workflow(checkpointer=checkpointer)

    input_state = {
        "messages": [{"role": "user", "content": message}],
        "filters": filters,
        "thread_id": id,
        "hitl_enabled": hitl_enabled,
    }

    result = await workflow.ainvoke(input_state, config=config)

    # 상태 확인
    snapshot = await workflow.aget_state(config)
    next_steps = snapshot.next

    status = "completed"
    if next_steps:
        status = "paused"

    return map_to_chat_response(result, status, next_steps)


@router.get("/sessions/{id}/trace", response_model=SessionTraceResponse)
async def get_session_trace(id: str, checkpointer=Depends(get_checkpointer)):
    """특정 세션의 대화 이력 및 상태 추적 (HITL 용)"""
    config = {"configurable": {"thread_id": id}}
    state = await checkpointer.aget(config)
    if not state:
        return SessionTraceResponse(messages=[], values={})

    values = state["channel_values"]
    messages = []
    # State messages are objects
    for m in values.get("messages", []):
        role = getattr(m, "type", "assistant")
        content = getattr(m, "content", str(m))
        messages.append(MessageDTO(role=role, content=content))

    return SessionTraceResponse(messages=messages, values={k: v for k, v in values.items() if k != "messages"})


@router.post("/feedback", response_model=BaseResponse)
async def save_feedback(feedback: dict[str, Any], service: Annotated[Feedback, Depends(get_feedback_service)]):
    """사용자 피드백 저장"""
    if service.save_feedback(feedback):
        return BaseResponse(message="Feedback saved successfully")
    raise HTTPException(status_code=500, detail="Failed to save feedback")


@router.post("/sessions/{id}/resume", response_model=ChatResponse, status_code=status.HTTP_202_ACCEPTED)
async def resume_session(
    id: str,
    payload: dict[str, Any],
    agent: Annotated[ConversationalRAGAgent, Depends(get_conversational_rag_agent)],
    checkpointer=Depends(get_checkpointer),
):
    """중단된 세션(HITL) 재개"""
    user_input = payload.get("input")
    if user_input is None:
        raise HTTPException(status_code=400, detail="Input is required")

    workflow = agent.build_workflow(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": id}}

    if user_input and user_input != "Approved":
        from langchain_core.messages import HumanMessage

        feedback_msg = HumanMessage(content=user_input)
        await workflow.aupdate_state(config, {"messages": [feedback_msg]})
        result = await workflow.ainvoke(None, config=config)
    else:
        result = await workflow.ainvoke(None, config=config)

    snapshot = await workflow.aget_state(config)
    next_steps = snapshot.next

    status = "completed"
    if next_steps:
        status = "paused"

    return map_to_chat_response(result, status, next_steps)


@router.post("/sessions/{id}/reset", response_model=BaseResponse)
async def reset_session(id: str, checkpointer=Depends(get_checkpointer)):
    """세션 상태 초기화"""
    # [Spec 060] AsyncPostgresSaver의 adelete_thread 사용
    # [Spec 060] AsyncPostgresSaver의 adelete_thread 사용
    if hasattr(checkpointer, "adelete_thread"):
        await checkpointer.adelete_thread(id)
        return BaseResponse(message=f"Session {id} reset successfully (History Deleted via adelete).")

    # [Spec 061] adelete_thread 미지원 시 SQL 직접 실행 (Fallback)
    from app.core import database

    if database.pool:
        async with database.pool.connection() as conn:
            # LangGraph Postgres Checkpointer Tables
            # Checkpoints, Writes, Blobs (if any associated with thread)
            # 순서: Child -> Parent (Writes -> Checkpoints)
            await conn.execute("DELETE FROM checkpoint_writes WHERE thread_id = %s", (id,))
            await conn.execute("DELETE FROM checkpoint_blobs WHERE thread_id = %s", (id,))
            await conn.execute("DELETE FROM checkpoints WHERE thread_id = %s", (id,))
            await conn.set_autocommit(True) # Ensure commit if not auto

        return BaseResponse(message=f"Session {id} reset successfully (History Deleted via SQL).")

    return BaseResponse(message=f"Session {id} reset requested (Not Supported by Checkpointer and no DB connection).")


@router.get("/threads", response_model=list[ThreadResponse])
async def list_threads(checkpointer=Depends(get_checkpointer)):
    """활성 스레드 목록 조회"""
    from app.infrastructure.ai.ingestion_orchestrator import IngestionOrchestrator
    from app.infrastructure.factories.llm_factory import LLMFactory

    adapter = IngestionOrchestrator(llm=LLMFactory.get_llm_adapter(), checkpointer=checkpointer)
    threads = await adapter.list_threads(limit=50)
    return [
        ThreadResponse(
            thread_id=t.config["configurable"]["thread_id"],
            checkpoint_id=t.checkpoint["id"],
            metadata=t.metadata,
        )
        for t in threads
    ]
