import asyncio
from app.infrastructure.scrapers.youtube_scraper import YouTubeScraper
from app.infrastructure.ai.langchain_extractor import LangChainExtractor
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import get_settings

async def test_scraper():
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL_NAME, google_api_key=settings.GEMINI_API_KEY)
    scraper = YouTubeScraper(llm=llm)
    
    url = "https://www.youtube.com/watch?v=ukmjb7xOaAg"
    print(f"Scraping {url}...")
    result = await scraper.scrape(url)
    
    print("\n--- Scraper Metadata ---")
    print(result.metadata)
    
    print("\n--- Scraper Title ---")
    print(result.metadata.get('title'))

if __name__ == "__main__":
    asyncio.run(test_scraper())
