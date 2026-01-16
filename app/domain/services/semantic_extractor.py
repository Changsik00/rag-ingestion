from typing import Optional
import logging
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.llm import get_llm
from app.domain.schemas.extraction import ExtractedMetadata

logger = logging.getLogger(__name__)

class SemanticExtractor:
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.llm = llm or get_llm()
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

    def extract(self, text: str) -> Optional[ExtractedMetadata]:
        """
        Extracts semantic metadata from the given text synchronously.
        Returns None if extraction fails.
        """
        try:
            # Gemini might have token limits, checking length might be good, 
            # but for now we rely on the model's capacity (approx 30k tokens for Pro).
            # We might want to truncate if it's too huge, but let's keep it simple for now.
            logger.info("Starting semantic extraction via LLM...")
            result = self.chain.invoke({"text": text})
            logger.info("Semantic extraction completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Failed to extract semantic metadata: {e}")
            return None
