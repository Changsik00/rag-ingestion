"""
Entity API Endpoints

Entity 기반 조회 및 Document 검색 API
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.schemas.ontology import RelationshipType
from app.interfaces.api.dependencies import get_graph_repository, get_repository

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("")
async def list_entities(
    graph: Annotated[GraphRepository, Depends(get_graph_repository)],
    limit: int = 100
):
    """전체 Entity 목록 조회 (type별 정렬)"""
    return graph.list_all_entities(limit=limit)


@router.get("/{name:path}/documents")
async def get_documents_by_entity(
    name: str,
    graph: Annotated[GraphRepository, Depends(get_graph_repository)],
    storage: Annotated[DocumentRepository, Depends(get_repository)]
):
    """특정 Entity가 언급된 Document 목록"""
    doc_ids = graph.get_document_ids_by_entity(name)

    # 실제 Document 조회
    docs = []
    for doc_id in doc_ids:
        try:
            doc = storage.get(UUID(doc_id))
            if doc:
                docs.append(doc)
        except ValueError:
            # Invalid UUID format
            continue

    return docs


@router.get("/{name:path}/info")
async def get_entity_info(
    name: str,
    graph: Annotated[GraphRepository, Depends(get_graph_repository)]
):
    """Entity 정보 및 관련 통계"""
    doc_ids = graph.get_document_ids_by_entity(name)

    return {
        "name": name,
        "mention_count": len(doc_ids),
        "document_ids": doc_ids
    }


@router.get("/{name:path}/relationships")
async def get_entity_relationships(
    name: str,
    graph: Annotated[GraphRepository, Depends(get_graph_repository)],
    relationship_type: str | None = None
):
    """
    Entity의 관계 목록 조회
    
    Args:
        name: Entity 이름 (예: "Elon Musk")
        relationship_type: 필터링할 관계 타입 (optional)
            - FOUNDED, WORKS_FOR, USES, RELATED_TO, SUPPORTS, PERFORMED, PART_OF
    
    Returns:
        List of relationships with target entity info
    
    Example:
        GET /entities/Elon%20Musk/relationships
        GET /entities/Tesla/relationships?relationship_type=USES
    """
    # Convert string to RelationshipType enum
    rel_type = None
    if relationship_type:
        try:
            rel_type = RelationshipType(relationship_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid relationship_type: {relationship_type}. "
                       f"Valid types: FOUNDED, WORKS_FOR, USES, RELATED_TO, SUPPORTS, PERFORMED, PART_OF"
            )
    
    return graph.get_entity_relationships(name, rel_type)
