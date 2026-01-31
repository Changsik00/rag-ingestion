import base64

import fitz
from neo4j import GraphDatabase


def check_extraction():
    uri = "bolt://neo4j:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

    with driver.session() as session:
        # Get the latest job with content
        result = session.run(
            "MATCH (j:IngestionJob) WHERE j.raw_content IS NOT NULL RETURN j.job_id, j.raw_content, j.filename ORDER BY j.created_at DESC LIMIT 1"
        )
        record = result.single()
        if not record:
            print("No job found with raw_content")
            return

        job_id = record["j.job_id"]
        filename = record["j.filename"]
        raw_content_b64 = record["j.raw_content"]

        print(f"Checking Job: {job_id}, Filename: {filename}")

        try:
            content = base64.b64decode(raw_content_b64)
            print(f"Content length: {len(content)} bytes")
            print(f"Header (PDF?): {content[:5]}")

            doc = fitz.open(stream=content, filetype="pdf")
            print(f"Pages: {len(doc)}")

            doc.close()

            # Check Document nodes
            print("\nChecking Document nodes...")
            result = session.run(
                "MATCH (d:Document) RETURN d.id, left(d.content, 100) as content ORDER BY d.created_at DESC LIMIT 3"
            )
            for rec in result:
                print(f"Doc ID: {rec['d.id']}, Content: {repr(rec['content'])}")

            # Check Chunk nodes
            print("\nChecking Chunk nodes...")
            result = session.run("MATCH (c:Chunk) RETURN c.chunk_id, left(c.content, 100) as content LIMIT 3")
            for rec in result:
                print(f"Chunk ID: {rec['c.chunk_id']}, Content: {repr(rec['content'])}")

        except Exception as e:
            print(f"Error: {e}")

    driver.close()


if __name__ == "__main__":
    check_extraction()
