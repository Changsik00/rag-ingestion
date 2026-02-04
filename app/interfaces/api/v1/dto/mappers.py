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
