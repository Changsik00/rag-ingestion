import os

from neo4j import GraphDatabase

# Environment variables (defaulting to docker-compose values if not set)
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def debug_print(msg):
    print(f"[DEBUG] {msg}")


def inspect_graph():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    with driver.session() as session:
        # 1. Check for Nodes
        debug_print("Checking for 'Elon' and 'Twitter' entities...")
        result = session.run("""
            MATCH (n:Entity)
            WHERE n.name CONTAINS '일론' OR n.name CONTAINS '트위터' OR n.name CONTAINS 'Elon' OR n.name CONTAINS 'Twitter'
            RETURN n.name, labels(n)
        """)
        nodes = [record["n.name"] for record in result]
        if not nodes:
            debug_print("❌ No matching entities found.")
        else:
            debug_print(f"✅ Found entities: {nodes}")

        # 2. Check for Direct Relationships
        if len(nodes) >= 2:
            debug_print("Checking for direct relationships between found entities...")
            result = session.run("""
                MATCH (a:Entity)-[r]-(b:Entity)
                WHERE (a.name CONTAINS '일론' OR a.name CONTAINS 'Elon')
                  AND (b.name CONTAINS '트위터' OR b.name CONTAINS 'Twitter')
                RETURN a.name, type(r), b.name
            """)
            rels = [f"{r['a.name']} -[{r['type(r)']}]-> {r['b.name']}" for r in result]
            if not rels:
                debug_print("❌ No direct relationships found.")
            else:
                debug_print("✅ Found relationships:\n" + "\n".join(rels))

            # 3. Check for Paths (up to 2 hops)
            debug_print("Checking for paths (up to 2 hops)...")
            result = session.run("""
                MATCH p = (a:Entity)-[*1..2]-(b:Entity)
                WHERE (a.name CONTAINS '일론' OR a.name CONTAINS 'Elon')
                  AND (b.name CONTAINS '트위터' OR b.name CONTAINS 'Twitter')
                RETURN [n in nodes(p) | n.name] as path
            """)
            paths = [str(r["path"]) for r in result]
            if not paths:
                debug_print("❌ No paths found (up to 2 hops).")
            else:
                debug_print("✅ Found paths:\n" + "\n".join(paths))

    driver.close()


if __name__ == "__main__":
    inspect_graph()
