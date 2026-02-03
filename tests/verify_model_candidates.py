import asyncio

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings


async def verify_models():
    settings = get_settings()
    api_key = settings.GEMINI_API_KEY

    candidates = [
        "gemini-3-flash-preview",
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
    ]

    print(f"--- Verifying Models with API Key (masked): {api_key[:5]}... ---")

    for model in candidates:
        print(f"\nTesting Model: {model}")
        try:
            llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.0, max_retries=1)
            response = await llm.ainvoke("Ping.")
            print(f"✅ SUCCESS: {model}")
            print(f"   Response: {response.content}")
            return  # Stop after finding the first working one? No, let's see which one user wants.
            # Actually user asked about gemini-3 specifically.

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                print(f"❌ NOT FOUND (404): {model}")
            elif "429" in error_msg:
                print(f"⚠️ RATE LIMITED (429): {model} (Exists but busy)")
            else:
                print(f"❌ FAILED: {model} - {e}")


if __name__ == "__main__":
    asyncio.run(verify_models())
