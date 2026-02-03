from app.infrastructure.repositories.chroma import ChromaVectorRepository
import json

def check_semantic_chunks():
    repo = ChromaVectorRepository()
    
    print(f"--- ChromaDB Status ---")
    collections = repo.client.list_collections()
    for coll in collections:
        count = coll.count()
        print(f"Collection: {coll.name}, Size: {count}")

    # 모든 청크 조회 (메타데이터 확인용)
    results = repo.collection.get(limit=10)
    
    if not results or not results["ids"]:
        print("No chunks found in 'documents' collection.")
        return

    print(f"\n--- Sample Metadatas from 'documents' ---")
    for i in range(len(results["ids"])):
        print(f"ID: {results['ids'][i]}")
        print(f"Metadata: {json.dumps(results['metadatas'][i], indent=2)}")

    print(f"--- ChromaDB Chunks (Latest {len(results['ids'])}) ---")
    for i in range(len(results["ids"])):
        content = results["documents"][i]
        meta = results["metadatas"][i]
        chunk_id = results["ids"][i]
        
        strategy = meta.get("chunking_strategy", "N/A")
        
        print(f"\n[ID: {chunk_id}]")
        print(f"Strategy: {strategy}")
        print(f"Length: {len(content)} characters")
        print(f"Content: {content[:150]}...")
        if "breakpoint_threshold_amount" in meta:
            print(f"Threshold: {meta.get('breakpoint_threshold_amount')}")

if __name__ == "__main__":
    check_semantic_chunks()
