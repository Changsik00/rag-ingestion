from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.services.admin_agent import AdminAgent
from app.domain.services.feedback_service import FeedbackService
from app.interfaces.api.dependencies import get_admin_agent, get_checkpointer, get_feedback_service, get_repository

router = APIRouter()


@router.get("/documents/autocomplete")
async def autocomplete_documents(
    q: str = Query(..., min_length=1), repository: Annotated[DocumentRepository, Depends(get_repository)] = None
):
    """검색어 기반 문서 제목 자동완성"""
    try:
        docs = repository.list_documents(limit=10, search_term=q)
        return [{"id": str(d.id), "title": d.metadata.get("title", "Untitled")} for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{id}/ask")
async def ask_agent(
    id: str,
    payload: dict[str, Any],
    agent: Annotated[AdminAgent, Depends(get_admin_agent)],
    checkpointer=Depends(get_checkpointer),
):
    """Admin Agent에게 질문을 던지고 결과를 반환 (HITL 지원 가능)"""
    message = payload.get("message")
    filters = payload.get("filters")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        # LangGraph Workflow 실행
        config = {"configurable": {"thread_id": id}}
        workflow = agent.build_workflow(checkpointer=checkpointer)

        # input state 구성
        input_state = {"messages": [{"role": "user", "content": message}], "filters": filters, "thread_id": id}

        # 마지막 노드 결과 반환
        result = await workflow.ainvoke(input_state, config=config)

        # AIMessage 객체를 직렬화 가능한 형식으로 변환
        output_messages = []
        for msg in result.get("messages", []):
            output_messages.append({"role": msg.type, "content": msg.content})

        return {"messages": output_messages, "context_data": result.get("context_data"), "intent": result.get("intent")}
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{id}/trace")
async def get_session_trace(id: str, checkpointer=Depends(get_checkpointer)):
    """특정 세션의 대화 이력 및 상태 추적 (HITL 용)"""
    try:
        config = {"configurable": {"thread_id": id}}
        state = await checkpointer.aget(config)
        if not state:
            return {"messages": [], "values": {}}

        # AIMessage 등을 직렬화
        values = state.values
        messages = []
        for m in values.get("messages", []):
            messages.append({"role": m.type, "content": m.content})

        return {"messages": messages, "values": {k: v for k, v in values.items() if k != "messages"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def save_feedback(feedback: dict[str, Any], service: Annotated[FeedbackService, Depends(get_feedback_service)]):
    """사용자 피드백 저장"""
    if service.save_feedback(feedback):
        return {"success": True}
    raise HTTPException(status_code=500, detail="Failed to save feedback")


@router.post("/sessions/{id}/resume")
async def resume_session(
    id: str,
    payload: dict[str, Any],
    agent: Annotated[AdminAgent, Depends(get_admin_agent)],
    checkpointer=Depends(get_checkpointer),
):
    """중단된 세션(HITL) 재개"""
    user_input = payload.get("input")
    if user_input is None:
        raise HTTPException(status_code=400, detail="Input is required")

    try:
        # Resume (State update or command)
        # LangGraph 0.2+ style: workflow.ainvoke(None, config) to resume from interrupt
        # or workflow.aupdate_state then ainvoke.
        # 기존 adapter의 resume 로직 참고
        from app.core.llm import get_llm
        from app.infrastructure.brain.adapter import LangGraphAdapter

        adapter = LangGraphAdapter(llm=get_llm(), checkpointer=checkpointer)
        result = await adapter.resume(id, user_input)

        return {"status": "Resumed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{id}/reset")
async def reset_session(id: str, checkpointer=Depends(get_checkpointer)):
    """세션 상태 초기화"""
    try:
        # SQLiteSaver 에서 해당 thread_id 데이터 삭제 로직 (Best effort)
        # 실제로는 새로운 thread_id 를 사용하도록 유도하는 것이 나음
        # 여기서는 placeholder
        return {"success": True, "message": f"Session {id} reset requested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads")
async def list_threads(checkpointer=Depends(get_checkpointer)):
    """활성 스레드 목록 조회"""
    try:
        from app.core.llm import get_llm
        from app.infrastructure.brain.adapter import LangGraphAdapter

        adapter = LangGraphAdapter(llm=get_llm(), checkpointer=checkpointer)
        threads = await adapter.list_threads(limit=50)
        return [
            {
                "thread_id": t.config["configurable"]["thread_id"],
                "checkpoint_id": t.checkpoint["id"],
                "metadata": t.metadata,
            }
            for t in threads
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
