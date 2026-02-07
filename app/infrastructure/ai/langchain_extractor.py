import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.value_objects.extracted_metadata import ExtractedMetadata

logger = logging.getLogger(__name__)


class LangChainExtractor:
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
            4. **Primary Entity**: Identify the MAIN SUBJECT or PROGRAM NAME this content belongs to.
               - Look for it in the 'SOURCE METADATA' (e.g., Program Name, Channel, Video Title).
               - If the content is a talk show fragment, this should be the Show Name (e.g., '어쩌다 어른'). 
               - If it's a biography, it should be the Person's Name.
            5. Key entities classified by EXACTLY one of the following standardized types:

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
            - **CRITICAL**: Use the provided 'SOURCE METADATA' (like Program Name, Channel, or Title) to determine the `primary_entity`.
            - Ensure the final Title, Summary, and `primary_entity` explicitly reflect the correct context.
            - If an entity could fit multiple types, prioritize based on context.
            - **If uncertain, use CONCEPT as the default fallback type.**
            - For Korean activity names like "벤치마킹" or "책 쓰기", use ACTIVITY type.
            - GPT-4 is a PRODUCT (commercial AI product), not TECHNOLOGY.
            - Book titles should use DOCUMENT type.

            6. **Relationships between entities:**
            Extract meaningful relationships between the identified entities.

            **Relationship Types:**
            - FOUNDED: Person founded Organization (e.g., "Elon Musk founded Tesla")
            - WORKS_FOR: Person works for Organization (e.g., "Jane works at Google")
            - ACQUIRED: Person/Organization acquired Organization (e.g., "Elon Musk acquired Twitter")
            - OWNS: Person/Organization owns Product/Organization (e.g., "Microsoft owns GitHub")
            - USES: Organization uses Technology (e.g., "Netflix uses Python")
            - RELATED_TO: Generic relationship between any entities (e.g., "AI is related to Ethics", "Elon is related to controversies")
            - SUPPORTS: Technology supports Activity (e.g., "Docker supports deployment")
            - PERFORMED: Person performed Activity (e.g., "Steve Jobs gave presentations")
            - PART_OF: Activity is part of Activity (e.g., "Testing is part of development")

            **Important**: Capture high-value relationships that describe interactions, ownership, or causality.

            Text to analyze:
            {text}

            {format_instructions}
            """,
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        self.chain = self.prompt | self.llm | self.parser

    def extract_metadata(self, text: str) -> ExtractedMetadata | None:
        """동기식 메타데이터 추출 (하위 호환용)"""
        try:
            logger.info("Starting semantic extraction via LLM (Sync)...")
            result = self.chain.invoke({"text": text})
            return result
        except Exception as e:
            logger.error(f"Failed to extract semantic metadata (Sync): {e}")
            return None

    async def aextract_metadata(self, text: str) -> ExtractedMetadata | None:
        """비동기식 메타데이터 추출"""
        try:
            logger.info("Starting semantic extraction via LLM (Async)...")
            result = await self.chain.ainvoke({"text": text})
            logger.info("Semantic extraction completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Failed to extract semantic metadata (Async): {e}")
            return None

    def generate(self, prompt: str) -> str:
        """단순 텍스트 생성 (동기)"""
        try:
            from langchain_core.output_parsers import StrOutputParser

            chain = self.llm | StrOutputParser()
            return chain.invoke(prompt)
        except Exception as e:
            logger.error(f"Failed to generate text (Sync): {e}")
            return f"Error: {str(e)}"

    async def agenerate(self, prompt: str) -> str:
        """단순 텍스트 생성 (비동기)"""
        try:
            from langchain_core.output_parsers import StrOutputParser

            chain = self.llm | StrOutputParser()
            return await chain.ainvoke(prompt)
        except Exception as e:
            logger.error(f"Failed to generate text (Async): {e}")
            return f"Error: {str(e)}"

    def bind(self, **kwargs):
        """LangChain Runnable binding delegation - Returns a new adapter instance"""
        bound_llm = self.llm.bind(**kwargs)
        return LangChainExtractor(bound_llm)

    def invoke(self, *args, **kwargs):
        return self.llm.invoke(*args, **kwargs)

    async def ainvoke(self, *args, **kwargs):
        return await self.llm.ainvoke(*args, **kwargs)
