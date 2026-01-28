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
    hitl_enabled = payload.get("hitl_enabled", False)

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        # LangGraph Workflow 실행
        config = {"configurable": {"thread_id": id}}
        workflow = agent.build_workflow(checkpointer=checkpointer)

        # input state 구성
        input_state = {
            "messages": [{"role": "user", "content": message}],
            "filters": filters,
            "thread_id": id,
            "hitl_enabled": hitl_enabled,
        }

        # 마지막 노드 결과 반환
        # ainvoke는 실행이 중단되거나 완료될 때까지 실행됨
        result = await workflow.ainvoke(input_state, config=config)

        # 상태 확인 (HITL 중단 여부 체크)
        snapshot = await workflow.aget_state(config)
        next_steps = snapshot.next

        status = "completed"
        if next_steps:
            status = "paused"

        # AIMessage 객체를 직렬화 가능한 형식으로 변환
        output_messages = []
        for msg in result.get("messages", []):
            output_messages.append({"role": msg.type, "content": msg.content})

        return {
            "messages": output_messages,
            "context_data": result.get("context_data"),
            "intent": result.get("intent"),
            "status": status,
            "next": next_steps,
        }
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
        values = state["channel_values"]
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
        # LangGraph 0.2+ style: workflow.ainvoke(Command(resume=v), config) to resume from interrupt

        # 1. Rebuild Workflow
        # checkpointer is required for resume
        workflow = agent.build_workflow(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": id}}

        # 2. Invoke with Command(resume=...)
        # The value passed to resume become the result of the interrupted node/edge?
        # For 'human_review' edge interruption or node interruption?
        # If we interrupted using interrupt_before=["human_review"], we are BEFORE the node.
        # But wait, AdminAgent logic uses conditional edge to "human_review".
        # And build_workflow sets interrupt_before=["human_review"].
        # So we are paused right before 'human_review' node executes.
        # If we send a Command(resume="Approved"), LangGraph will continue execution.
        # However, ainvoke might need None as input if we just want to proceed, OR updates if we want to change state.

        # If we use `Command(resume="value")`, this value is returned by the `interrupt` call inside a node.
        # BUT we are using `interrupt_before`.
        # When using `interrupt_before`, we usually just invoke with None to proceed, OR invoke with state update to change state.
        # To pass feedback, we likely want to update the state (e.g. `tool_output` or `messages`) before proceeding.

        # Let's try invoke(None) first, but wait, the user provided input (e.g. "Approved" or feedback).
        # We should probably update the state with this feedback.
        # AdminState has 'tool_output'. Let's update that? Or add a message?

        # 2. Handle Feedback vs Approval
        if user_input and user_input != "Approved":
            # Feedback provided: Add as HumanMessage to state
            from langchain_core.messages import HumanMessage

            feedback_msg = HumanMessage(content=user_input)
            await workflow.aupdate_state(config, {"messages": [feedback_msg]})

            # Resume execution (will route to router due to new message)
            result = await workflow.ainvoke(None, config=config)
        else:
            # Approval: Just resume (will route to END)
            result = await workflow.ainvoke(None, config=config)

        # Status Check to ensure it finished or paused again
        snapshot = await workflow.aget_state(config)
        next_steps = snapshot.next

        status = "completed"
        if next_steps:
            status = "paused"

        output_messages = []
        for msg in result.get("messages", []):
            output_messages.append({"role": msg.type, "content": msg.content})

        return {
            "status": status,
            "result": {
                "messages": output_messages,
                "context_data": result.get("context_data"),
                "intent": result.get("intent"),
            },
        }
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
