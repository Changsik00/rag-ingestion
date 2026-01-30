from typing import Protocol, Any


class LLMInterface(Protocol):
    """Protocol for LLM adapters"""
    
    async def ainvoke(self, messages: Any) -> Any:
        """Asynchronously invoke the LLM with messages"""
        ...
    
    def invoke(self, messages: Any) -> Any:
        """Synchronously invoke the LLM with messages"""
        ...
