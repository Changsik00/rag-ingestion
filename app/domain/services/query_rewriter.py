import logging
from app.domain.interfaces.llm import LLMInterface

logger = logging.getLogger(__name__)

class QueryRewriter:
    """
    대화 이력(History)을 기반으로 현재 질문(Query)을
    검색 가능한 독립적 쿼리(Standalone Query)로 재구성하는 서비스
    """
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        
    def rewrite(self, query: str, history: list[dict]) -> str:
        """
        Args:
            query: 사용자의 현재 질문
            history: 대화 이력 리스트 [{"role": "user", "content": "..."}, ...]
            
        Returns:
            str: 재구성된 쿼리 (또는 원본 쿼리)
        """
        # 1. 히스토리가 없으면 원본 즉시 반환 (비용 절감)
        if not history:
            logger.debug("No history found. Returning original query.")
            return query
            
        # 2. 최근 5턴만 유지 (너무 길면 노이즈)
        recent_history = history[-10:] # 5 turns (pairs)
        
        # 3. 프롬프트 구성
        history_text = ""
        for msg in recent_history:
            role = "Human" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"
            
        prompt = f"""
Given the following conversation history and a follow-up question, rephrase the follow-up question to be a standalone question.
Answer in the SAME LANGUAGE as the follow-up question.

Chat History:
{history_text}
Follow Up Input: {query}
Standalone Question:"""

        # 4. LLM 호출
        try:
            logger.info("Rewriting query with context...")
            rewritten_query = self.llm.generate(prompt).strip()
            
            # 후처리: LLM이 가끔 "Standalone Question: " 등을 포함할 수 있음
            if "Standalone Question:" in rewritten_query:
                rewritten_query = rewritten_query.split("Standalone Question:")[-1].strip()
                
            logger.info(f"Original: {query} -> Rewritten: {rewritten_query}")
            return rewritten_query
            
        except Exception as e:
            logger.error(f"Failed to rewrite query: {e}. Falling back to original.")
            return query
