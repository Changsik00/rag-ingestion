from typing import Any

from app.interfaces.api.v1.dto.rag import ChatResponse, MessageDTO


class ChatResponseMapper:
    @staticmethod
    def map_graph_output_to_response(result: dict, status: str, next_steps: Any) -> ChatResponse:
        output_messages = []
        # result['messages'] might be AIMessage objects or dicts (ainvoke returns dict? output checks msg.type)
        # LangGraph returns objects in "messages" usually.
        for msg in result.get("messages", []):
            role = getattr(msg, "type", "assistant")
            if role == "human":
                role = "user"
            if role in ["ai", "assistant"]:
                role = "assistant"
            content = getattr(msg, "content", str(msg))
            output_messages.append(MessageDTO(role=role, content=content))

        # [Bug Fix] Explicitly serialize pydantic models in context_data
        # Otherwise, they might be empty in the JSON response
        raw_context = result.get("context_data") or {}
        serializable_context = {}
        if isinstance(raw_context, dict):
            for k, v in raw_context.items():
                if hasattr(v, "model_dump"):
                    serializable_context[k] = v.model_dump()
                elif isinstance(v, list):
                    serializable_context[k] = [
                        item.model_dump() if hasattr(item, "model_dump") else item 
                        for item in v
                    ]
                else:
                    serializable_context[k] = v

        return ChatResponse(
            current_status=status,
            messages=output_messages,
            context_data=serializable_context,
            intent=result.get("intent"),
            next=list(next_steps) if next_steps else None,
            draft_content=result.get("draft_content"),
            is_clarification=result.get("is_clarification", False),
            missing_slots=result.get("missing_slots"),
        )
