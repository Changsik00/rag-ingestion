import json
from uuid import UUID

from neo4j import Driver

from app.core.exceptions import InfrastructureException
from app.core.logging_config import setup_logger
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import DocumentRepository

logger = setup_logger(__name__)


class Neo4jStorage(DocumentRepository):
    def __init__(self, driver: Driver):
        self.driver = driver

    def close(self):
        self.driver.close()

    def _flatten_metadata(self, metadata: dict) -> dict:
        """Neo4j 호환을 위해 메타데이터 평탄화"""
        flattened = {}
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                flattened[f"{key}_json"] = json.dumps(value)
            else:
                flattened[key] = value
        return flattened

    def save(self, document: Document) -> None:
        try:
            flattened_metadata = self._flatten_metadata(document.metadata)

            query = """
            MERGE (d:Document {id: $id})
            SET d.content = $content,
                d.created_at = $created_at,
                d += $metadata
            """
            # source_url is now part of metadata or handled if it exists.
            # Our new Document entity removed source_url and put it in metadata?
            # Let's check Document entity definition again.
            # Document entity has `content` and `metadata`. `source_url` was removed from field list in my edit?
            # Yes, I removed explicit `source_url` field in Step 181.
            # I must ensure it is saved in metadata if present.

            with self.driver.session() as session:
                session.run(
                    query,
                    id=str(document.id),
                    content=document.content,
                    created_at=document.created_at.isoformat(),
                    metadata=flattened_metadata,
                )
        except Exception as e:
            logger.error(f"Failed to save document to Neo4j: {e}")
            raise InfrastructureException(f"Failed to save document to Neo4j: {e}") from e

    def save_with_chunks(self, document: Document, chunks: list[Chunk]) -> None:
        """문서와 청크를 함께 저장하고 관계를 형성합니다."""
        try:
            # 1. 문서 저장 (기존 로직 재사용 가능하거나 통합)
            self.save(document)

            # 2. 청크 저장 및 관계 생성
            query = """
            MATCH (d:Document {id: $doc_id})
            UNWIND $chunks AS chunk_data
            MERGE (c:Chunk {id: chunk_data.id})
            SET c.content = chunk_data.content,
                c.index = chunk_data.index,
                c.parent_id = $doc_id,
                c += chunk_data.metadata
            MERGE (d)-[:HAS_CHUNK]->(c)
            """

            # Prepare chunks data
            chunks_data = []
            for chunk in chunks:
                chunk_dict = {
                    "id": chunk.id,
                    "content": chunk.content,
                    "index": chunk.index,
                    "metadata": self._flatten_metadata(chunk.metadata),
                }
                chunks_data.append(chunk_dict)

            with self.driver.session() as session:
                session.run(query, doc_id=document.id, chunks=chunks_data)

        except Exception as e:
            logger.error(f"Failed to save chunks to Neo4j: {e}")
            raise InfrastructureException(f"Failed to save chunks to Neo4j: {e}") from e

    def get(self, doc_id: UUID) -> Document | None:
        try:
            query = "MATCH (d:Document {id: $id}) RETURN d"
            with self.driver.session() as session:
                result = session.run(query, id=str(doc_id)).single()
                if result:
                    node = result["d"]
                    return Document(
                        id=str(node["id"]),  # Ensure ID is string for Pydantic
                        content=node.get("content", ""),
                        # source_url removal handled by not mapping it explicitly
                        metadata={k: v for k, v in node.items() if k not in ["id", "content", "created_at"]},
                        created_at=node.get("created_at"),  # Pydantic will handle parsing if isoformat string
                    )
            return None
        except Exception as e:
            logger.error(f"Failed to get document from Neo4j (id={doc_id}): {e}")
            raise InfrastructureException(f"Failed to get document from Neo4j: {e}") from e

    def list_documents(self, limit: int = 10, search_term: str | None = None) -> list[Document]:
        """
        List documents with optional case-insensitive search (LIKE style).
        """
        try:
            where_clause = ""
            params = {"limit": limit}
            if search_term:
                # Case-insensitive substring match using regex
                # Neo4j regex syntax: =~ '(?i).*term.*'
                where_clause = "WHERE d.title =~ $regex OR d.source =~ $regex"
                params["regex"] = f"(?i).*{search_term}.*"

            query = f"MATCH (d:Document) {where_clause} RETURN d ORDER BY d.created_at DESC LIMIT $limit"
            docs = []
            with self.driver.session() as session:
                results = session.run(query, **params)
                for record in results:
                    node = record["d"]
                    docs.append(
                        Document(
                            id=node["id"],
                            content=node.get("content", ""),
                            metadata={k: v for k, v in node.items() if k not in ["id", "content", "created_at"]},
                        )
                    )
            return docs
        except Exception as e:
            logger.error(f"Failed to list documents from Neo4j: {e}")
            raise InfrastructureException(f"Failed to list documents from Neo4j: {e}") from e

    def get_chunks(self, doc_id: UUID) -> list[Chunk]:
        try:
            query = """
            MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK]->(c:Chunk)
            RETURN c
            ORDER BY c.index ASC
            """
            chunks = []
            with self.driver.session() as session:
                results = session.run(query, doc_id=str(doc_id))
                for record in results:
                    node = record["c"]

                    # Unflatten metadata (Reuse logic if possible, or duplicate for now due to helper method privacy)
                    metadata = {}
                    for k, v in node.items():
                        if k in ["id", "content", "index", "parent_id"]:
                            continue
                        if k.endswith("_json"):
                            try:
                                clean_key = k[:-5]
                                metadata[clean_key] = json.loads(v)
                            except (ValueError, TypeError):
                                metadata[k] = v
                        else:
                            metadata[k] = v

                    chunks.append(
                        Chunk(
                            id=node["id"],
                            content=node.get("content", ""),
                            parent_id=node.get("parent_id"),
                            index=node.get("index", 0),
                            metadata=metadata
                        )
                    )
            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks from Neo4j: {e}")
            raise InfrastructureException(f"Failed to get chunks from Neo4j: {e}") from e

    def create_fulltext_index(self):
        """Chunk Content에 대한 Fulltext Index 생성"""
        try:
            # Neo4j 5.x syntax might differ, using generic robust syntax or 5.x specific
            # Using 5.x syntax: CREATE FULLTEXT INDEX ... FOR (n:Label) ON EACH [n.prop]
            query = """
            CREATE FULLTEXT INDEX chunk_fulltext IF NOT EXISTS
            FOR (c:Chunk) ON EACH [c.content]
            """
            with self.driver.session() as session:
                session.run(query)
        except Exception as e:
            logger.error(f"Failed to create fulltext index: {e}")
            raise InfrastructureException(f"Failed to create fulltext index: {e}") from e

    def search(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        """Fulltext Index를 이용한 키워드 검색"""
        try:
            # 기본 Cypher Query
            # Note: 5.x Fulltext index does not support WHERE clause directly inside call queryNodes in legacy way?
            # Actually, we can filter AFTER yielding nodes.
            # "CALL ... YIELD node WHERE ..." is the standard pattern.

            where_clauses = []
            params = {"keyword": query, "limit": limit}

            if filters:
                for key, value in filters.items():
                    # Sanitize key to prevent excessive injection (basic check)
                    # Assuming keys are safe (e.g. doc_id, source)
                    
                    # Map 'doc_id' to internal 'id' or 'parent_id'? 
                    # Chunk has 'parent_id' which links to Document ID.
                    # DocumentRepository.search usually searches Chunks.
                    # So filtering by 'doc_id' usually means filtering by Chunk's parent_id.
                    
                    # Property name mapping:
                    target_prop = "parent_id" if key == "doc_id" else key
                    
                    param_key = f"filter_{key}"
                    params[param_key] = value
                    
                    if isinstance(value, list):
                         where_clauses.append(f"node.{target_prop} IN ${param_key}")
                    else:
                         where_clauses.append(f"node.{target_prop} = ${param_key}")

            where_snippet = " AND ".join(where_clauses)
            if where_snippet:
                where_snippet = f"WHERE {where_snippet}"
            
            cypher_query = f"""
            CALL db.index.fulltext.queryNodes("chunk_fulltext", $keyword) YIELD node, score
            {where_snippet}
            RETURN node, score
            LIMIT $limit
            """

            chunks = []
            with self.driver.session() as session:
                results = session.run(cypher_query, **params)
                for record in results:
                    node = record["node"]
                    # Map Neo4j Node to Chunk Entity
                    
                    # Unflatten metadata
                    metadata = {}
                    for k, v in node.items():
                        if k in ["id", "content", "index", "parent_id"]:
                            continue
                        if k.endswith("_json"):
                            try:
                                clean_key = k[:-5]
                                metadata[clean_key] = json.loads(v)
                            except (ValueError, TypeError):
                                metadata[k] = v
                        else:
                            metadata[k] = v

                    chunks.append(
                        Chunk(
                            id=node["id"],
                            content=node.get("content", ""),
                            parent_id=node.get("parent_id"),
                            index=node.get("index", 0),
                            metadata=metadata
                        )
                    )
            return chunks

        except Exception as e:
            logger.error(f"Neo4j search failed: {e}")
            logger.warning(f"Neo4j Search Error: {e}")
            return []
