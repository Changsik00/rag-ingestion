import os
import sys
from uuid import UUID

# Create a fake module structure to allow imports if running from script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.interfaces.api.dependencies import get_neo4j_driver


def dump_full_document(doc_id_str=None):
    print("Initializing Neo4j Connection...")
    driver = get_neo4j_driver()
    repo = Neo4jStorage(driver)

    try:
        if not doc_id_str:
            print("\n📚 List of Recent Documents:")
            docs = repo.list_documents(limit=10)

            if not docs:
                print("No documents found.")
                return

            for i, doc in enumerate(docs):
                title = doc.metadata.get("title", "No Title")
                url = doc.metadata.get("url", doc.metadata.get("source_url", "No URL"))
                print(f"[{i}] {title} ({url}) - ID: {doc.id}")

            selection = input("\nEnter document index or ID to dump: ")

            try:
                idx = int(selection)
                if 0 <= idx < len(docs):
                    doc_id_str = str(docs[idx].id)
            except ValueError:
                doc_id_str = selection

        print(f"\n🔍 Fetching full document for ID: {doc_id_str}...")
        try:
            target_uuid = UUID(doc_id_str)
        except ValueError:
            print("❌ Invalid UUID format.")
            return

        doc = repo.get(target_uuid)

        if not doc:
            print("⚠️ Document not found.")
            return

        output_filename = "scraped_content.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(doc.content)

        print(f"✅ Full content saved to: {os.path.abspath(output_filename)}")
        print("=" * 80)
        print(f"Title: {doc.metadata.get('title')}")
        print(f"URL: {doc.metadata.get('url')}")
        print("=" * 80)
        print("Preview (First 1000 chars):")
        print(doc.content[:1000])
        print("...")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        repo.close()


if __name__ == "__main__":
    target_id = None
    if len(sys.argv) > 1:
        target_id = sys.argv[1]

    dump_full_document(target_id)
