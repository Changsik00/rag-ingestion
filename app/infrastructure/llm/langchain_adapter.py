import logging
from typing import Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.schemas.extraction import ExtractedMetadata

logger = logging.getLogger(__name__)


class LangChainLLMAdapter:
    """
    LangChain을 LLMInterface에 맞게 변환하는 어댑터
    
    Infrastructure 레이어에 위치하여 Domain을 외부 프레임워크로부터 격리.
    기존 SemanticExtractor의 LangChain 로직을 이곳으로 이동.
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Args:
            llm: LangChain의 ChatGoogleGenerativeAI 클라이언트
        """
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ExtractedMetadata)
        self.prompt = PromptTemplate(
            template="""
            You are an advanced AI assistant capable of analyzing text and extracting structured metadata.
            
            Please analyze the following text and extract:
            1. A suitable title (if the original is missing or unclear).
            2. A concise summary (approx. 3 sentences).
            3. A list of 5-10 relevant keywords.
            4. Key entities classified by type (Person, Organization, Technology, Topic, etc.).
            
            Focus on capturing the core meaning and most important entities.
            
            Text to analyze:
            {text}
            
            {format_instructions}
            """,
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | self.parser
    
    def extract_metadata(self, text: str) -> Optional[ExtractedMetadata]:
        """
        LLMInterface 구현: 텍스트에서 메타데이터 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            ExtractedMetadata: 추출된 메타데이터
            None: 추출 실패 시
        """
        try:
            logger.info("Starting semantic extraction via LLM...")
            result = self.chain.invoke({"text": text})
            logger.info("Semantic extraction completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Failed to extract semantic metadata: {e}")
            return None
