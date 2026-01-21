from neo4j import GraphDatabase

from app.admin.config import AdminConfig


class GraphService:
    def __init__(self):
        self.config = AdminConfig()
        self.driver = GraphDatabase.driver(
            self.config.neo4j_uri, auth=(self.config.neo4j_username, self.config.neo4j_password)
        )

    def close(self):
        self.driver.close()

    def get_presets(self) -> dict[str, str]:
        return {
            "전체 노드 조회 (Limit 50)": "MATCH (n) RETURN n LIMIT 50",
            "문서-청크 포함 조회": "MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk) RETURN d, c LIMIT 20",
            "사람(Person) 간 관계 조회": "MATCH (p1:Person)-[r]->(p2:Person) RETURN p1, r, p2 LIMIT 50",
            "기술(Technology) 관련 문서": "MATCH (t:Technology)<-[:MENTIONS]-(d:Document) RETURN t, d LIMIT 50",
            "최근 수집된 문서 10건": "MATCH (d:Document) RETURN d ORDER BY d.created_at DESC LIMIT 10",
        }

    def build_query(self, entity_type: str = "All", relation_type: str = "All", limit: int = 50) -> str:
        query_parts = []

        # Base Match
        if entity_type == "All":
            if relation_type == "All":
                query_parts.append("MATCH (n)-[r]->(m)")
                query_parts.append("RETURN n, r, m")
            else:
                query_parts.append(f"MATCH (n)-[r:{relation_type}]->(m)")
                query_parts.append("RETURN n, r, m")
        else:
            if relation_type == "All" or relation_type is None:
                query_parts.append(f"MATCH (n:{entity_type})")
                query_parts.append("RETURN n")
            else:
                query_parts.append(f"MATCH (n:{entity_type})-[r:{relation_type}]->(m)")
                query_parts.append("RETURN n, r, m")

        # Limit
        query_parts.append(f"LIMIT {limit}")

        return " ".join(query_parts)

    def execute_query(self, query: str) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def execute_graph_query(self, query: str) -> tuple[list[dict], list[dict]]:
        with self.driver.session() as session:
            result = session.run(query)
            graph = result.graph()

            nodes = []
            for node in graph.nodes:
                nodes.append({"id": node.element_id, "labels": list(node.labels), "properties": dict(node._properties)})

            edges = []
            for rel in graph.relationships:
                edges.append(
                    {
                        "id": rel.element_id,
                        "source": rel.start_node.element_id,
                        "target": rel.end_node.element_id,
                        "type": rel.type,
                        "properties": dict(rel._properties),
                    }
                )

            return nodes, edges
