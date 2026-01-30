import asyncio
import os

from neo4j import GraphDatabase


async def reset_all():
    # 1. Reset Neo4j
    uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    print(f"Connecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Neo4j reset complete.")
    driver.close()

    # 2. Reset Chroma (Delete collection)
    print("Resetting ChromaDB...")
    try:
        # We can't easily use dependencies outside of FastAPI context without a lot of setup,
        # so let's use a simpler direct client call inside the container environment.
        import chromadb

        host = os.getenv("CHROMA_HOST", "rag-chroma")
        port = int(os.getenv("CHROMA_PORT", 8000))
        client = chromadb.HttpClient(host=host, port=port)

        # Delete the specific collection
        try:
            client.delete_collection("documents")
            print("Chroma collection 'documents' deleted.")
        except Exception as e:
            print(f"Could not delete 'documents' (might not exist): {e}")

    except Exception as e:
        print(f"Chroma reset failed: {e}")


if __name__ == "__main__":
    asyncio.run(reset_all())
