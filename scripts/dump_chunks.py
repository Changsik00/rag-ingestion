import sys
import os
from uuid import UUID

# Create a fake module structure to allow imports if running from script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.interfaces.api.dependencies import get_neo4j_driver

def dump_chunks():
    print("Initializing Neo4j Connection...")
    driver = get_neo4j_driver()
    repo = Neo4jStorage(driver)

    try:
        print("\n📚 List of Recent Documents:")
        docs = repo.list_documents(limit=10)
        
        if not docs:
            print("No documents found.")
            return

        for i, doc in enumerate(docs):
            # Try to get title or url from metadata
            title = doc.metadata.get("title", "No Title")
            url = doc.metadata.get("url", doc.metadata.get("source_url", "No URL"))
            print(f"[{i}] {title} ({url}) - ID: {doc.id}")

        selection = None
        if len(sys.argv) > 1:
            selection = sys.argv[1]
        else:
            selection = input("\nEnter document index or ID to view chunks: ")
        
        target_doc_id = None
        try:
            idx = int(selection)
            if 0 <= idx < len(docs):
                target_doc_id = docs[idx].id
        except ValueError:
            try:
                target_doc_id = UUID(selection)
            except ValueError:
                pass
        
        if not target_doc_id:
            print("❌ Invalid selection.")
            return

        print(f"\n🔍 Fetching chunks for Document ID: {target_doc_id}...")
        chunks = repo.get_chunks(target_doc_id)
        
        if not chunks:
            print("⚠️ No chunks found for this document.")
            return

        print(f"✅ Found {len(chunks)} chunks:\n")
        print("="*80)
        for chunk in chunks:
            print(f"🧩 Chunk #{chunk.index} (ID: {chunk.id})")
            print(f"Metadata: {chunk.metadata}")
            print("-" * 40)
            print(chunk.content)
            print("="*80)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        repo.close()

if __name__ == "__main__":
    dump_chunks()
