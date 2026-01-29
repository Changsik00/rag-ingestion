import os

from dotenv import load_dotenv

# Load .env file explicitly
from app.core.config import get_settings
from app.core.llm import LLMFactory

load_dotenv()

settings = get_settings()

TEST_TEXT = """
일론 리브 머스크(영어: Elon Reeve Musk, 1971년 6월 28일 ~ )는 남아프리카 공화국 출신의 미국의 기업인이다. 
페이팔의 전신이 된 온라인 결제 서비스 회사 x.com, 로켓 제조 회사 겸 민간 우주 기업 스페이스X, 
전기 자동차 회사 테슬라 등을 설립했다. 
2022년 10월 트위터를 인수한 후 CEO 재직 후 사임하였다.
"""

async def test_extraction():
    print("Initializing LLM Adapter...")
    try:
        adapter = LLMFactory.get_llm_adapter()
        print("Extracting metadata...")
        result = adapter.extract_metadata(TEST_TEXT)

        if result:
            print("\n=== Extraction Result ===")
            print(f"Entities: {result.entities}")
            print(f"Relationships: {result.relationships}")
        else:
            print("Extraction failed (returned None).")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not set. Please set it to run the script.")
    else:
        # LangChainLLMAdapter.extract_metadata is synchronous in its current implementation (invokes chain)
        # But let's run it simply.
        adapter = LLMFactory.get_llm_adapter()
        result = adapter.extract_metadata(TEST_TEXT)
        if result:
            print("\n=== Extraction Result ===")
            print(f"Entities: {result.entities}")
            print(f"Relationships: {result.relationships}")
        else:
            print("Extraction failed.")
