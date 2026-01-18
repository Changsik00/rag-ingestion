import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
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
            4. Key entities classified by EXACTLY one of the following standardized types:

            **CRITICAL: Entity Classification Rules**
            You MUST classify entities into EXACTLY one of these 9 types:

            - PERSON: Individual people or fictional characters
              Examples: "Elon Musk", "Geoffrey Hinton", "Steve Jobs", "Harry Potter"

            - ORGANIZATION: Companies, institutions, or groups
              Examples: "Tesla", "MIT", "World Health Organization", "Y Combinator"

            - TECHNOLOGY: Specific tools, frameworks, languages, or technical products
              Examples: "Python", "Docker", "Neo4j", "React", "PostgreSQL"

            - CONCEPT: Abstract ideas, theories, methodologies, or academic concepts
              Examples: "Machine Learning", "Clean Architecture", "Quantum Computing", "Lean Startup"
              **IMPORTANT**: Use CONCEPT as a fallback if uncertain about the entity type.

            - LOCATION: Geographic locations, cities, regions, or countries
              Examples: "Seoul", "Silicon Valley", "United States", "San Francisco"

            - EVENT: Specific events, conferences, or historical moments
              Examples: "OpenAI DevDay 2024", "World War II", "NeurIPS 2024"

            - ACTIVITY: Actions, tasks, processes, or work activities
              Examples: "책 쓰기", "벤치마킹", "코드 리뷰", "데이터 분석", "프로토타이핑", "A/B 테스팅"

            - PRODUCT: Physical or digital products, commercial goods
              Examples: "iPhone", "Tesla Model 3", "GPT-4", "Microsoft Office", "PlayStation 5"

            - DOCUMENT: Papers, books, reports, or written works
              Examples: "Clean Code", "Attention Is All You Need", "The Lean Startup", "research paper"

            **Important Guidelines**:
            - If an entity could fit multiple types, prioritize based on context.
            - **If uncertain, use CONCEPT as the default fallback type.**
            - For Korean activity names like "벤치마킹" or "책 쓰기", use ACTIVITY type.
            - GPT-4 is a PRODUCT (commercial AI product), not TECHNOLOGY.
            - Book titles should use DOCUMENT type.

            Text to analyze:
            {text}

            {format_instructions}
            """,
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | self.parser

    def extract_metadata(self, text: str) -> ExtractedMetadata | None:
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
