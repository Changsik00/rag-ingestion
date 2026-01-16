import os
import sys

# Add project root to sys.path to ensure imports work
sys.path.append(os.getcwd())

from dotenv import load_dotenv
from app.domain.services.semantic_extractor import SemanticExtractor
from app.core.llm import get_llm

def test_extraction():
    # Load .env manually to ensure the key is available
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment.")
        return

    print(f"🔑 API Key found: {api_key[:5]}...{api_key[-5:]}")
    
    # Inject LLM adapter
    llm_adapter = get_llm()
    extractor = SemanticExtractor(llm=llm_adapter)
    
    text = """
    LangChain is a framework for developing applications powered by language models. 
    It enables applications that:
    - Are context-aware: connect a language model to sources of context (prompt instructions, few shot examples, content to ground its response in, etc.)
    - Reason: rely on a language model to reason (about how to answer based on provided context, what actions to take, etc.)
    
    SpaceX is an American spacecraft manufacturer, launch service provider and satellite communications company headquartered in Hawthorne, California. 
    It was founded in 2002 by Elon Musk with the goal of reducing space transportation costs to enable the colonization of Mars.
    """
    
    print("\n🚀 Sending text to SemanticExtractor (Gemini)...")
    try:
        metadata = extractor.extract(text)
        
        if metadata:
            print("\n✅ Extraction Successful!")
            print(f"Title: {metadata.title}")
            print(f"Summary: {metadata.summary}")
            print("Keywords:", metadata.keywords)
            print("Entities:", metadata.entities)
        else:
            print("\n❌ Extraction returned None.")
            
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")

if __name__ == "__main__":
    test_extraction()
