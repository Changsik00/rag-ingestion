import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.infrastructure.repositories.chroma import ChromaVectorRepository

async def inspect_specific_chunk(chunk_id: str):
    print(f"\n=== Inspecting Chunk ID: {chunk_id} ===\n")
    try:
        chroma_repo = ChromaVectorRepository()
        result = chroma_repo.collection.get(ids=[chunk_id], include=["metadatas", "documents"])
        
        if result and result["ids"]:
            doc = result["documents"][0]
            meta = result["metadatas"][0]
            print(f"ID: {chunk_id}")
            print(f"Title: {meta.get('title')}")
            print(f"Source: {meta.get('source')}")
            print(f"Content: {doc}")
            print("-" * 50)
            
            # Find neighbors by parent_id?
            pid = meta.get('parent_id')
            if pid:
                print(f"\nFinding other chunks with Parent ID: {pid}")
                neighbors = chroma_repo.collection.get(where={"parent_id": pid}, include=["metadatas"])
                print(f"Total chunks for this document: {len(neighbors['ids'])}")
                for i in range(min(5, len(neighbors['ids']))):
                     print(f"- {neighbors['ids'][i]}: {neighbors['metadatas'][i].get('title')} (Index: {neighbors['metadatas'][i].get('index')})")
        else:
            print(f"Chunk ID {chunk_id} not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # The ID confirmed from previous logs
    target_id = "63f39b69-3154-4109-b6f0-3910f8e6cd52"
    asyncio.run(inspect_specific_chunk(target_id))
