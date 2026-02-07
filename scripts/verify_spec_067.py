import asyncio
from uuid import uuid4
from app.domain.value_objects.chunk import Chunk
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository
from neo4j import GraphDatabase
import os

async def verify_spec_067():
    print("🚀 Verifying Spec-067: Advanced Reranking & Context Expansion")
    
    # 1. Setup Neo4j
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    auth = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
    driver = GraphDatabase.driver(uri, auth=auth)
    repo = Neo4jDocumentRepository(driver)
    
    doc_id = str(uuid4())
    print(f"📄 Creating dummy document with chunks: {doc_id}")
    
    # Create sequential chunks
    chunks = [
        Chunk(id=f"c-{doc_id}-0", content="The capital of France is Paris.", parent_id=doc_id, index=0, metadata={}),
        Chunk(id=f"c-{doc_id}-1", content="It is known for the Eiffel Tower.", parent_id=doc_id, index=1, metadata={}),
        Chunk(id=f"c-{doc_id}-2", content="The Louvre museum is also there.", parent_id=doc_id, index=2, metadata={}),
    ]
    
    from app.domain.entities.document import Document
    doc = Document(id=doc_id, content="History of Paris", metadata={"source_id": "test-067"})
    
    repo.save_with_chunks(doc, chunks)
    
    # 2. Verify Context Expansion
    print("\n🔍 Testing get_adjacent_chunks...")
    adj = repo.get_adjacent_chunks(doc_id, index=1, window_size=1)
    
    print(f"Found {len(adj)} adjacent chunks.")
    for c in adj:
        print(f"Index {c.index}: {c.content}")
        
    assert len(adj) == 3, f"Expected 3 chunks, got {len(adj)}"
    assert adj[0].index == 0
    assert adj[2].index == 2
    
    print("✅ get_adjacent_chunks verified successfully!")
    driver.close()

if __name__ == "__main__":
    asyncio.run(verify_spec_067())
