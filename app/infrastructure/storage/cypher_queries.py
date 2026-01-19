"""Cypher query templates for Knowledge Graph operations"""

# Entity 관련 쿼리
MERGE_ENTITY = """
MERGE (e:Entity {name: $name})
ON CREATE SET
    e.type = $type,
    e.normalized_name = toLower($name),
    e.created_at = datetime()
RETURN e.name as name
"""

CREATE_ENTITY_INDEX = """
CREATE CONSTRAINT entity_name_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.name IS UNIQUE
"""

# 관계 관련 쿼리
CREATE_MENTIONS_RELATIONSHIP = """
MATCH (d:Document {id: $doc_id})
MATCH (e:Entity {name: $entity_name})
MERGE (d)-[r:MENTIONS]->(e)
ON CREATE SET r.created_at = datetime()
"""

# 조회 쿼리
GET_ENTITIES_BY_DOCUMENT = """
MATCH (d:Document {id: $doc_id})-[:MENTIONS]->(e:Entity)
RETURN e.name as name, e.type as type
"""

GET_DOCUMENT_IDS_BY_ENTITY = """
MATCH (e:Entity {name: $entity_name})<-[:MENTIONS]-(d:Document)
RETURN d.id as doc_id
"""

# ===== Entity-Entity Relationship Queries (Spec 016) =====

CREATE_ENTITY_RELATIONSHIP = """
MATCH (source:Entity {name: $source_name})
MATCH (target:Entity {name: $target_name})
MERGE (source)-[r:{relationship_type}]->(target)
ON CREATE SET r.created_at = datetime()
RETURN type(r) as relationship_type
"""

GET_ENTITY_RELATIONSHIPS = """
MATCH (e:Entity {name: $entity_name})-[r]->(target:Entity)
RETURN type(r) as relationship_type,
       target.name as target_name,
       target.type as target_type
"""

GET_ENTITY_RELATIONSHIPS_BY_TYPE = """
MATCH (e:Entity {name: $entity_name})-[r:{relationship_type}]->(target:Entity)
RETURN type(r) as relationship_type,
       target.name as target_name,
       target.type as target_type
"""

LIST_ALL_ENTITIES = """
MATCH (e:Entity)
RETURN e.name as name, e.type as type
ORDER BY e.type, e.name
LIMIT $limit
"""
