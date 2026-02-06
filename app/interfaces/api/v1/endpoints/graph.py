from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from neo4j import Driver

from app.interfaces.api.dependencies import get_neo4j_driver
from app.interfaces.api.v1.dto.graph import GraphPresetResponse, GraphQueryResponse, GraphSchemaResponse

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


@router.get("/presets", response_model=GraphPresetResponse)
async def get_presets():
    """자주 사용하는 Cypher 쿼리 프리셋 조회"""
    return GraphPresetResponse(
        presets={
            "전체 노드/관계 조회 (Limit 50)": "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50",
            "문서-청크 포함 조회": "MATCH (d:Document)-[r:HAS_CHUNK]->(c:Chunk) RETURN d, r, c LIMIT 20",
            "사람(Person) 간 관계 조회": "MATCH (p1:Person)-[r]->(p2:Person) RETURN p1, r, p2 LIMIT 50",
            "기술(Technology) 관련 문서": "MATCH (t:Technology)<-[:MENTIONS]-(d:Document) RETURN t, d LIMIT 50",
            "최근 수집된 문서 10건": "MATCH (d:Document) RETURN d ORDER BY d.created_at DESC LIMIT 10",
        }
    )


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
            nodes.append(
                {
                    "id": node.element_id,
                    "labels": list(node.labels),
                    "properties": _sanitize_props(dict(node._properties)),
                }
            )

        edges = []
        for rel in graph.relationships:
            edges.append(
                {
                    "id": rel.element_id,
                    "source": rel.start_node.element_id,
                    "target": rel.end_node.element_id,
                    "type": rel.type,
                    "properties": _sanitize_props(dict(rel._properties)),
                }
            )

        return GraphQueryResponse(nodes=nodes, edges=edges)


def _sanitize_props(props: dict) -> dict:
    """Neo4j 전용 타입(DateTime 등)을 JSON 직렬화 가능하도록 변환"""
    new_props = {}
    for k, v in props.items():
        if hasattr(v, "iso_format"):  # DateTime, Date, Time
            new_props[k] = v.iso_format()
        elif hasattr(v, "to_iso8601"):  # Duration in some versions?
            new_props[k] = v.to_iso8601()
        else:
            new_props[k] = str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v
    return new_props
