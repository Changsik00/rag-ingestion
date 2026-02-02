from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from neo4j import Driver

from app.interfaces.api.dependencies import get_neo4j_driver
from app.interfaces.api.v1.dto.graph import GraphQueryResponse, GraphSchemaResponse

router = APIRouter(tags=["Graph"])


@router.get("/schema", response_model=GraphSchemaResponse)
async def get_schema(driver: Annotated[Driver, Depends(get_neo4j_driver)]):
    """지석 그래프 노드 라벨 및 관계 타입 조회"""
    with driver.session() as session:
        labels_res = session.run("CALL db.labels()")
        labels = [record[0] for record in labels_res]

        rels_res = session.run("CALL db.relationshipTypes()")
        rels = [record[0] for record in rels_res]

        return GraphSchemaResponse(labels=labels, relationship_types=rels)


@router.get("/presets")
async def get_presets():
    """자주 사용하는 Cypher 쿼리 프리셋 조회"""
    return {
        "전체 노드 조회 (Limit 50)": "MATCH (n) RETURN n LIMIT 50",
        "문서-청크 포함 조회": "MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk) RETURN d, c LIMIT 20",
        "사람(Person) 간 관계 조회": "MATCH (p1:Person)-[r]->(p2:Person) RETURN p1, r, p2 LIMIT 50",
        "기술(Technology) 관련 문서": "MATCH (t:Technology)<-[:MENTIONS]-(d:Document) RETURN t, d LIMIT 50",
        "최근 수집된 문서 10건": "MATCH (d:Document) RETURN d ORDER BY d.created_at DESC LIMIT 10",
    }


@router.post("/query", response_model=GraphQueryResponse)
async def execute_query(query: dict[str, str], driver: Annotated[Driver, Depends(get_neo4j_driver)]):
    """Cypher 쿼리 실행 후 agraph 형식(nodes, edges)으로 변환하여 반환"""
    cypher = query.get("query")
    if not cypher:
        raise HTTPException(status_code=400, detail="Query is required")

    with driver.session() as session:
        result = session.run(cypher)
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

        return GraphQueryResponse(nodes=nodes, edges=edges)
