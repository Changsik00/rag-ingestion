
import asyncio
from app.infrastructure.factories.llm_factory import LLMFactory
from app.core.config import get_settings

async def verify():
    settings = get_settings()
    print(f"Testing LLM Model: {settings.GEMINI_MODEL_NAME}")
    print(f"Testing Embedding Model: {settings.GEMINI_EMBEDDING_MODEL_NAME}")
    
    try:
        # Test LLM
        llm = LLMFactory.get_google_llm(temperature=0.0)
        print("Invoking LLM...")
        response = await llm.ainvoke("Hello, are you operational? Reply with 'YES'.")
        print(f"LLM Response: {response.content}")
        print("✅ LLM Connection Successful")
        
    except Exception as e:
        print(f"❌ LLM Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
