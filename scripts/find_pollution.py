import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.infrastructure.repositories.chroma import ChromaVectorRepository

async def find_polluted_chunks():
    keywords = ["Elon", "Musk", "SpaceX", "Tesla", "Steve", "Jobs", "Apple"]
    print(f"\n=== Searching ChromaDB for Keywords: {keywords} ===\n")
    try:
        chroma_repo = ChromaVectorRepository()
        
        # We can't use query() with embedding failures, but we can use get() with a where clause on content?
        # Actually, ChromaDB 'get' where only works on metadatas.
        # So we have to fetch all metadatas and search.
        
        # Performance warning: get(include=['metadatas', 'documents']) might be heavy if DB is huge.
        # But for this dev env, it should be fine.
        results = chroma_repo.collection.get(include=["metadatas", "documents"])
        
        found_count = 0
        if results and results["ids"]:
            for i in range(len(results["ids"])):
                cid = results["ids"][i]
                doc = results["documents"][i].lower()
                meta = results["metadatas"][i]
                title = meta.get('title', '').lower()
                
                match = any(k.lower() in doc or k.lower() in title for k in keywords)
                
                if match:
                    found_count += 1
                    print(f"[{found_count}] Found Match: ID: {cid}")
                    print(f"    Title: {meta.get('title')}")
                    print(f"    Source: {meta.get('source')}")
                    print(f"    Snippet: {doc[:150].replace('\n', ' ')}...")
                    print("-" * 50)
                    if found_count >= 20: 
                        print("... Too many matches found, truncating display.")
                        break
        
        print(f"\nTotal matches found: {found_count}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(find_polluted_chunks())
