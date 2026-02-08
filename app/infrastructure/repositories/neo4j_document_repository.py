import json
from datetime import datetime
from uuid import UUID

from neo4j import Driver

from app.core.logger import setup_logger
from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.value_objects.chunk import Chunk
from app.infrastructure.exceptions import InfrastructureError

logger = setup_logger(__name__)


class Neo4jDocumentRepository(DocumentRepository):
    def __init__(self, driver: Driver):
        self.driver = driver

    def close(self):
        self.driver.close()

    def reset_database(self) -> None:
        """모든 데이터(Node, Relationship)를 삭제하여 DB를 초기화합니다. (주의: 복구 불가)"""
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            logger.warning("Neo4j Database has been reset (All nodes and relationships deleted).")
        except Exception as e:
            logger.error(f"Failed to reset Neo4j database: {e}")
            raise InfrastructureError(f"Failed to reset Neo4j database: {e}") from e

    def _flatten_metadata(self, metadata: dict) -> dict:
        """Neo4j 호환을 위해 메타데이터 평탄화"""
        flattened = {}
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                flattened[f"{key}_json"] = json.dumps(value)
            else:
                flattened[key] = value
        return flattened

    def _unflatten_metadata(self, node_items: dict) -> dict:
        """Neo4j 속성을 도메인 메타데이터로 복원 (json 해제 등)"""
        metadata = {}
        for k, v in node_items.items():
            if k in ["id", "content", "created_at", "updated_at"]:
                continue
            if isinstance(v, str) and k.endswith("_json"):
                try:
                    metadata[k[:-5]] = json.loads(v)
                except (ValueError, TypeError):
                    metadata[k] = v
            else:
                metadata[k] = v

        # [Spec-054] Ensure source_id exists for DocumentMetadata validation
        if "source_id" not in metadata:
            metadata["source_id"] = (
                metadata.get("url") or metadata.get("source") or node_items.get("id", "unknown_source")
            )

        return metadata

    def save(self, document: Document) -> None:
        try:
            # DocumentMetadata -> dict 변환
            meta_dict = (
                document.metadata.model_dump() if hasattr(document.metadata, "model_dump") else document.metadata
            )
            flattened_metadata = self._flatten_metadata(meta_dict)

            query = """
            MERGE (d:Document {id: $id})
            SET d.content = $content,
                d.created_at = $created_at,
                d.primary_entity = $primary_entity,
                d += $metadata
            """
            # source_url is now part of metadata or handled if it exists.
            # Our new Document entity removed source_url and put it in metadata?
            # Let's check Document entity definition again.
            # Document entity has `content` and `metadata`. `source_url` was removed from field list in my edit?
            # Yes, I removed explicit `source_url` field in Step 181.
            # I must ensure it is saved in metadata if present.

            # created_at 안전하게 처리
            from datetime import datetime

            c_at = document.created_at
            if isinstance(c_at, str):
                created_at_str = c_at
            elif isinstance(c_at, datetime):
                created_at_str = c_at.isoformat()
            else:
                created_at_str = datetime.now().isoformat()

            with self.driver.session() as session:
                session.run(
                    query,
                    id=str(document.id),
                    content=document.content,
                    created_at=created_at_str,
                    primary_entity=flattened_metadata.get("primary_entity"),
                    metadata=flattened_metadata,
                )
        except Exception as e:
            logger.error(f"Failed to save document to Neo4j: {e}")
            raise InfrastructureError(f"Failed to save document to Neo4j: {e}") from e

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
            raise InfrastructureError(f"Failed to save chunks to Neo4j: {e}") from e

    def get(self, doc_id: UUID) -> Document | None:
        try:
            query = "MATCH (d:Document {id: $id}) RETURN d"
            with self.driver.session() as session:
                result = session.run(query, id=str(doc_id)).single()
                if result:
                    node = result["d"]
                    return Document(
                        id=node["id"],
                        content=node.get("content", ""),
                        metadata=self._unflatten_metadata(node),
                        created_at=node.get("created_at") or datetime.now(),
                    )
            return None
        except Exception as e:
            logger.error(f"Failed to get document from Neo4j (id={doc_id}): {e}")
            raise InfrastructureError(f"Failed to get document from Neo4j: {e}") from e

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
                            metadata=self._unflatten_metadata(node),
                            created_at=node.get("created_at") or datetime.now(),
                        )
                    )
            return docs
        except Exception as e:
            logger.error(f"Failed to list documents from Neo4j: {e}")
            raise InfrastructureError(f"Failed to list documents from Neo4j: {e}") from e

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
                    chunks.append(
                        Chunk(
                            id=node["id"],
                            content=node.get("content", ""),
                            parent_id=node.get("parent_id"),
                            index=node.get("index", 0),
                            metadata=self._unflatten_metadata(node),
                        )
                    )
            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks from Neo4j: {e}")
            raise InfrastructureError(f"Failed to get chunks from Neo4j: {e}") from e

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
            raise InfrastructureError(f"Failed to create fulltext index: {e}") from e

    def search(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        """Fulltext Index를 이용한 키워드 검색"""
        try:
            # 기본 Cypher Query
            # Note: 5.x Fulltext index does not support WHERE clause directly inside call queryNodes in legacy way?
            # Actually, we can filter AFTER yielding nodes.
            # "CALL ... YIELD node WHERE ..." is the standard pattern.

            # [Spec 066 Fix] Escape Lucene special characters in query
            # ( ) [ ] { } ^ " ~ * ? : \ /
            escaped_query = query
            for char in r'()[]{}^"~*?:\/':
                escaped_query = escaped_query.replace(char, f"\\{char}")

            # Remove Lucene keywords AND/OR if they appear as standalone words to prevent syntax error
            import re

            escaped_query = re.sub(r"\b(AND|OR|NOT)\b", lambda m: m.group(1).lower(), escaped_query)

            where_clauses = []
            params = {"keyword": escaped_query, "limit": limit}

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

            where_snippet = " AND ".join(where_clauses) if where_clauses else ""
            if where_snippet:
                where_snippet = "WHERE " + where_snippet

            # [Spec 066 Fix] Score Thresholding for Keyword Search
            # Lucene scores below 1.0 are typically very weak/random noise.
            # Adding score filter to where_snippet
            if where_snippet:
                where_snippet += " AND score > 1.0"
            else:
                where_snippet = "WHERE score > 1.0"

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
                    score = record["score"]
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

                    # Add search score for tracing
                    metadata["score"] = score

                    chunks.append(
                        Chunk(
                            id=node["id"],
                            content=node.get("content", ""),
                            parent_id=node.get("parent_id"),
                            index=node.get("index", 0),
                            metadata=metadata,
                        )
                    )
            return chunks

        except Exception as e:
            logger.error(f"Neo4j search failed: {e}")
            logger.warning(f"Neo4j Search Error: {e}")
            return []

    def get_all_chunk_ids(self) -> set[str]:
        """Neo4j의 모든 청크 ID를 가져옵니다."""
        try:
            query = "MATCH (c:Chunk) RETURN c.id as id"
            with self.driver.session() as session:
                result = session.run(query)
                # Ensure we only return strings and filter out None
                return {str(record["id"]) for record in result if record["id"]}
        except Exception as e:
            logger.error(f"Failed to get all chunk IDs from Neo4j: {e}")
            return set()

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[Chunk]:
        """여러 청크 ID에 해당하는 청크들을 한 번에 가져옵니다."""
        try:
            query = """
            MATCH (c:Chunk)
            WHERE c.id IN $ids
            RETURN c
            """
            chunks = []
            with self.driver.session() as session:
                results = session.run(query, ids=chunk_ids)
                for record in results:
                    node = record["c"]
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
                            metadata=self._unflatten_metadata(node),
                        )
                    )
            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks by IDs from Neo4j: {e}")
            return []

    def get_adjacent_chunks(self, parent_id: str, index: int, window_size: int = 1) -> list[Chunk]:
        """주어진 인덱스 전후의 인접 청크들을 가져옵니다."""
        try:
            # Pivot chunk를 포함하여 [index-window, index+window] 범위 조회
            query = """
            MATCH (c:Chunk {parent_id: $parent_id})
            WHERE c.index >= $start AND c.index <= $end
            RETURN c
            ORDER BY c.index ASC
            """
            start = max(0, index - window_size)
            end = index + window_size

            chunks = []
            with self.driver.session() as session:
                results = session.run(query, parent_id=str(parent_id), start=start, end=end)
                for record in results:
                    node = record["c"]
                    chunks.append(
                        Chunk(
                            id=node["id"],
                            content=node.get("content", ""),
                            parent_id=node.get("parent_id"),
                            index=node.get("index", 0),
                            metadata=self._unflatten_metadata(node),
                        )
                    )
            return chunks
        except Exception as e:
            logger.error(f"Failed to get adjacent chunks for {parent_id} index {index}: {e}")
            return []

    def get_document_stats(self) -> list[dict]:
        """문서별 기본 통계를 가장 가볍고 빠르게 가져옵니다. (안정성 보장 버전)"""
        try:
            # 1. 문서 정보 가져오기 (가장 가벼운 프로퍼티만)
            # source_url 프로퍼티도 함께 조회
            query = "MATCH (d:Document) RETURN d.id as id, d.title as title, d.source as source, d.url as url, d.source_url as source_url"
            stats = []
            with self.driver.session() as session:
                results = session.run(query)
                for record in results:
                    if not record["id"]:
                        continue
                    stats.append(
                        {
                            "id": record["id"],
                            "title": record["title"] or "Untitled",
                            "url": record["source_url"] or record["source"] or record["url"] or "",
                            "chunk_count": 0,
                        }
                    )

            # 2. 청크 개수 합산 (관계 기반이 아닌 프로퍼티 기반으로 더 가볍게 시도하거나 MATCH (d)-[:HAS_CHUNK]->(c) 사용)
            # 여기서는 parent_id 프로퍼티를 사용하여 메모리 오버헤드 최소화
            count_query = "MATCH (c:Chunk) RETURN c.parent_id as pid, count(c) as cnt"
            with self.driver.session() as session:
                counts = session.run(count_query)
                count_map = {str(r["pid"]): r["cnt"] for r in counts}

            for s in stats:
                pid_str = str(s["id"])
                s["chunk_count"] = count_map.get(pid_str, 0)

            return stats
        except Exception as e:
            logger.error(f"Failed to get document stats from Neo4j: {e}")
            return []

    def get_all_chunk_metadata(self) -> list[dict]:
        """모든 청크의 핵심 데이터(ID, 부모 ID)를 조인 없이 가볍게 가져옵니다."""
        try:
            # content는 벌크 로드에서 제외 (성능 저하 방지)
            query = "MATCH (c:Chunk) RETURN c.id as id, c.parent_id as parent_id"
            with self.driver.session() as session:
                results = session.run(query)
                return [{"id": record["id"], "parent_id": record["parent_id"]} for record in results if record["id"]]
        except Exception as e:
            logger.error(f"Failed to get all chunk metadata from Neo4j: {e}")
            return []

    def get_all_source_names(self) -> list[str]:
        """
        Neo4j에 저장된 모든 고유한 Source 이름 목록을 반환합니다.
        
        Spec 073: Fuzzy Filter Matching을 위한 Available Sources 조회용.
        Document와 Chunk 양쪽에서 source를 조회하여 결합합니다.
        
        Returns:
            list[str]: Source 이름 목록 (중복 제거, 정렬)
        """
        try:
            # Document와 Chunk 양쪽에서 source 조회
            query = """
            MATCH (d:Document)
            WHERE d.source IS NOT NULL
            RETURN DISTINCT d.source AS source
            UNION
            MATCH (c:Chunk)
            WHERE c.source IS NOT NULL
            RETURN DISTINCT c.source AS source
            ORDER BY source
            """
            
            with self.driver.session() as session:
                result = session.run(query)
                sources = [record["source"] for record in result if record["source"]]
                logger.info(f"Found {len(sources)} unique sources in Neo4j: {sources[:5]}...")
                return sources
                
        except Exception as e:
            logger.error(f"Failed to get source names from Neo4j: {e}")
            return []
