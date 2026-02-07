import asyncio
from app.infrastructure.ai.langchain_extractor import LangChainExtractor
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import get_settings

async def main():
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME, 
        google_api_key=settings.GEMINI_API_KEY
    )
    extractor = LangChainExtractor(llm)
    test_text = "세상을 바꾸는 시간 15분, 줄여서 세바시에 나오게 되어 영광입니다. 오늘은 도파민 중독에 대해 이야기해보겠습니다."
    
    print("Testing extraction...")
    res = await extractor.aextract_metadata(test_text)
    if res:
        print(f"TITLE: {res.title}")
        print(f"SUMMARY: {res.summary}")
        print(f"PRIMARY ENTITY: {res.primary_entity}")
        print(f"ALIASES: {res.aliases}")
        print(f"KEYWORDS: {res.keywords}")
    else:
        print("EXTRACTION FAILED")

if __name__ == "__main__":
    asyncio.run(main())
