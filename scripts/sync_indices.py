
import asyncio
import os
import sys
from uuid import UUID
from tqdm import tqdm

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import get_settings
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.domain.entities.chunk import Chunk
from neo4j import GraphDatabase

async def main():
    settings = get_settings()
    
    # 1. Initialize Repositories
    chroma = ChromaStorage()
    
    driver = GraphDatabase.driver(
        settings.NEO4J_URI, 
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    # Using the driver directly for better control over IDs
    
    print("--- 🔍 Data Integrity Sync Starting ---")
    
    # 2. Get All Neo4j Chunk IDs
    with driver.session() as session:
        result = session.run("MATCH (c:Chunk) RETURN c.id as id")
        neo4j_ids = {record["id"] for record in result}
    
    print(f"Neo4j Total Chunks: {len(neo4j_ids)}")
    
    # 3. Get All Chroma Chunk IDs
    # Chroma get(include=[]) is standard
    chroma_result = chroma.collection.get(include=[])
    chroma_ids = set(chroma_result["ids"])
    print(f"Chroma Total Chunks: {len(chroma_ids)}")
    
    # 4. Find Missing
    missing_ids = neo4j_ids - chroma_ids
    print(f"Missing Chunks in Chroma: {len(missing_ids)}")
    
    if not missing_ids:
        print("✅ Everything is in sync!")
        driver.close()
        return

    # 5. Fetch and Re-index
    print(f"🚀 Re-indexing {len(missing_ids)} chunks...")
    
    batch_size = 20
    missing_list = list(missing_ids)
    
    for i in tqdm(range(0, len(missing_list), batch_size)):
        batch_ids = missing_list[i:i + batch_size]
        
        chunks_to_index = []
        with driver.session() as session:
            # Fetch content and metadata for this batch
            result = session.run(
                "MATCH (c:Chunk) WHERE c.id IN $ids RETURN c", 
                ids=batch_ids
            )
            for record in result:
                node = record["c"]
                # Convert Neo4j node to Chunk entity
                # Reconstruct metadata (it might be flattened in Neo4j depending on implementation)
                metadata = dict(node)
                # Remove internal properties
                metadata.pop("id", None)
                metadata.pop("content", None)
                metadata.pop("parent_id", None)
                metadata.pop("index", None)
                
                chunks_to_index.append(
                    Chunk(
                        id=UUID(node["id"]),
                        content=node["content"],
                        parent_id=UUID(node["parent_id"]) if node.get("parent_id") else None,
                        index=node.get("index", 0),
                        metadata=metadata
                    )
                )
        
        if chunks_to_index:
            try:
                chroma.save_chunks(chunks_to_index)
            except Exception as e:
                print(f"❌ Batch save failed: {e}")
                # Individual retries are handled in chroma.save_chunks now
    
    print("--- 🎉 Sync Completed ---")
    driver.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
