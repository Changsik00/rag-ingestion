from typing import Dict, Any, List, Optional
from app.domain.ingestion.state import IngestionState
from app.domain.interfaces.llm import LLMInterface

class IngestionNodes:
    """
    LangGraph의 각 노드에서 실행될 비즈니스 로직을 캡슐화한 클래스.
    Clean Architecture의 Use Case/Domain Logic에 해당하며,
    State를 입력받아 State Update를 반환합니다.
    """

    def __init__(self, llm: LLMInterface):
        self.llm = llm

    async def extract_metadata(self, state: IngestionState) -> Dict[str, Any]:
        """
        Raw Content에서 메타데이터(Title, Summary, Entities 등)를 추출합니다.
        
        Args:
            state (IngestionState): 현재 파이프라인 상태
            
        Returns:
            Dict[str, Any]: 상태 업데이트 (metadata, steps_history)
        """
        raw_content = state["raw_content"]
        
        # LLM 호출 (Synchronous call)
        # NOTE: LLMInterface가 현재 동기식이므로, 추후 비동기 전환 시 await loop.run_in_executor() 등 고려 필요
        extracted = self.llm.extract_metadata(raw_content)
        
        # ExtractedMetadata -> Dict 변환
        metadata_dict = extracted.model_dump() if extracted else {}
        
        # History 업데이트
        current_history = state.get("steps_history", [])
        new_history = current_history + ["extract_metadata"]
        
        return {
            "metadata": metadata_dict,
            "steps_history": new_history
        }

    def validate_content(self, state: IngestionState) -> Dict[str, Any]:
        """
        추출된 콘텐츠의 유효성을 검사합니다.
        (현재는 Placeholder implementation)
        """
        current_history = state.get("steps_history", [])
        new_history = current_history + ["validate_content"]
        
        return {"steps_history": new_history}
