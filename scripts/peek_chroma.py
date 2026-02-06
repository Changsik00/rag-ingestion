import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.infrastructure.repositories.chroma import ChromaVectorRepository

async def list_top_chunks():
    print("\n=== Listing Top 50 Chunks from ChromaDB documents collection ===\n")
    try:
        chroma_repo = ChromaVectorRepository()
        # peek() gives the first N items
        results = chroma_repo.collection.peek(limit=50)
        
        if results and results["ids"]:
            for i in range(len(results["ids"])):
                cid = results["ids"][i]
                doc = results["documents"][i]
                meta = results["metadatas"][i]
                
                print(f"[{i+1}] ID: {cid} | Title: {meta.get('title', 'N/A')} | Source: {meta.get('source', 'N/A')}")
                print(f"    Snippet: {doc[:150].replace('\n', ' ')}...")
                print("-" * 50)
        else:
            print("No chunks found in the collection.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_top_chunks())
