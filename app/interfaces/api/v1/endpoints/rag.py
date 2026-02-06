from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.agent import ConversationalRAGAgent
from app.application.services.feedback import Feedback
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.session_repository import SessionRepository
from app.interfaces.api.dependencies import (
    get_checkpointer,
    get_conversational_rag_agent,
    get_feedback_service,
    get_repository,
    get_session_repository,
)
from app.interfaces.api.v1.dto.common import BaseResponse
from app.interfaces.api.v1.dto.jobs import ThreadResponse
from app.interfaces.api.v1.dto.mappers import ChatResponseMapper
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


@router.post("/sessions/{id}/ask", response_model=ChatResponse, status_code=status.HTTP_202_ACCEPTED)
async def ask_agent(
    id: str,
    payload: ChatRequest,
    agent: Annotated[ConversationalRAGAgent, Depends(get_conversational_rag_agent)],
    checkpointer=Depends(get_checkpointer),
):
    """Conversational RAG Agent에게 질문을 던지고 결과를 반환 (HITL 지원 가능)"""
    # Spec 055: Advanced Settings Extraction
    retrieval_config = payload.advanced_settings.model_dump()

    # Spec 062: Service Facade Call
    result_dict = await agent.ask(
        thread_id=id,
        message=payload.message,
        filters=payload.filters,
        hitl_enabled=payload.hitl_enabled,
        retrieval_config=retrieval_config,
        checkpointer=checkpointer,
    )

    return ChatResponseMapper.map_graph_output_to_response(
        result_dict["result"], result_dict["status"], result_dict["next_steps"]
    )


@router.get("/sessions/{id}/trace", response_model=SessionTraceResponse)
async def get_session_trace(id: str, checkpointer=Depends(get_checkpointer)):
    """특정 세션의 대화 이력 및 상태 추적 (HITL 용)"""
    config = {"configurable": {"thread_id": id}}
    state = await checkpointer.aget(config)
    if not state:
        return SessionTraceResponse(messages=[], values={})

    # [Bug Fix] LangGraph state extraction logic
    # checkpointer.aget returns a dict or CheckpointTuple with 'checkpoint' attribute
    checkpoint = getattr(state, "checkpoint", state.get("checkpoint") if isinstance(state, dict) else {})
    values = checkpoint.get("channel_values", checkpoint.get("values", {}))
    
    if not values and isinstance(state, dict):
        # Fallback for alternative structures
        values = state.get("channel_values", state.get("values", {}))

    messages = []
    # State messages are objects (BaseMessage)
    for m in values.get("messages", []):
        # Try to extract role and content safely
        role = "assistant"
        if hasattr(m, "type"):
            role = m.type
        elif isinstance(m, dict):
            role = m.get("role", m.get("type", "assistant"))
            
        content = ""
        if hasattr(m, "content"):
            content = m.content
        elif isinstance(m, dict):
            content = m.get("content", str(m))
        else:
            content = str(m)
            
        messages.append(MessageDTO(role=role, content=content))

    return SessionTraceResponse(
        messages=messages, 
        values={k: v for k, v in values.items() if k != "messages"}
    )


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

    # Spec 062: Service Facade Call
    result_dict = await agent.resume(thread_id=id, user_input=user_input, checkpointer=checkpointer)

    return ChatResponseMapper.map_graph_output_to_response(
        result_dict["result"], result_dict["status"], result_dict["next_steps"]
    )


@router.post("/sessions/{id}/reset", response_model=BaseResponse)
async def reset_session(id: str, repository: Annotated[SessionRepository, Depends(get_session_repository)]):
    """세션 상태 초기화"""
    # Spec 062: Use Repository
    await repository.delete_session(id)
    return BaseResponse(message=f"Session {id} reset successfully (History Deleted via Repository).")


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
