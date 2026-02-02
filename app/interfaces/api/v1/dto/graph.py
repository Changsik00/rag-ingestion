from pydantic import BaseModel, Field


class GraphSchemaResponse(BaseModel):
    labels: list[str] = Field(..., description="List of node labels in the graph")
    relationship_types: list[str] = Field(..., description="List of relationship types in the graph")


class GraphNodeDTO(BaseModel):
    id: str
    labels: list[str]
    properties: dict


class GraphEdgeDTO(BaseModel):
    id: str
    source: str
    target: str
    type: str
    properties: dict


class GraphQueryResponse(BaseModel):
    nodes: list[GraphNodeDTO]
    edges: list[GraphEdgeDTO]


class GraphPresetResponse(BaseModel):
    presets: dict[str, str]
