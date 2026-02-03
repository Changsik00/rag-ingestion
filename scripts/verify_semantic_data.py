from app.interfaces.api.dependencies import get_neo4j_driver
from app.infrastructure.repositories.chroma import ChromaVectorRepository
import json

def find_and_verify():
    driver = get_neo4j_driver()
    chroma_repo = ChromaVectorRepository()
    
    with driver.session() as session:
        # Document 노드 검사 (메타데이터에 청킹 정보가 있는지 확인)
        result = session.run("MATCH (d:Document) RETURN d ORDER BY d.created_at DESC LIMIT 5")
        print("--- Recent Documents (Neo4j Direct) ---")
        for record in result:
            doc = record["d"]
            print(f"ID: {doc.get('id')}, Title: {doc.get('title')}")
            print(f"Metadata: {doc.get('metadata')}")
            
            # ChromaDB에서 해당 문서의 청크 확인
            parent_id = doc.get('id')
            results = chroma_repo.collection.get(
                where={"parent_id": str(parent_id)}
            )
            if results and results["ids"]:
                print(f"  => Found {len(results['ids'])} chunks in Chroma.")
                for i in range(min(2, len(results["ids"]))):
                    meta = results["metadatas"][i]
                    print(f"     [Chunk {i}] Strategy: {meta.get('chunking_strategy')}, Length: {len(results['documents'][i])}")
            else:
                print("  => No chunks found in Chroma.")

if __name__ == "__main__":
    find_and_verify()
