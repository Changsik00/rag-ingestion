import json
from uuid import UUID

import chromadb
from chromadb.utils import embedding_functions
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import get_settings
from app.infrastructure.exceptions import InfrastructureException
from app.core.logger import setup_logger
from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.value_objects.chunk import Chunk

logger = setup_logger(__name__)


class ChromaVectorRepository(DocumentRepository):
    def __init__(self):
        settings = get_settings()

        host = settings.CHROMA_HOST
        port = settings.CHROMA_PORT
        self.batch_size = settings.CHROMA_BATCH_SIZE
        self.client = chromadb.HttpClient(host=host, port=port)

        # Gemini Embedding API 설정
        gemini_api_key = settings.GEMINI_API_KEY
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required for ChromaDB embedding")

        # LangChain GoogleGenerativeAIEmbeddings를 ChromaDB embedding function wrapper로 변환
        langchain_embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", google_api_key=gemini_api_key
        )

        # ChromaDB가 요구하는 embedding function 형식으로 래핑
        class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
            def __call__(self, input: list[str]) -> list[list[float]]:
                # LangChain의 embed_documents 메서드 사용
                return langchain_embeddings.embed_documents(input)

        gemini_ef = GeminiEmbeddingFunction()

        self.embedding_function = gemini_ef

        self.collection = self.client.get_or_create_collection(
            name="documents", embedding_function=self.embedding_function
        )

    def reset_collection(self) -> None:
        """컬렉션을 삭제하고 재생성하여 데이터를 초기화합니다."""
        try:
            self.client.delete_collection(name="documents")
            self.collection = self.client.get_or_create_collection(
                name="documents", embedding_function=self.embedding_function
            )
            logger.warning("ChromaDB Collection 'documents' has been reset.")
        except Exception as e:
            logger.error(f"Failed to reset ChromaDB collection: {e}")
            raise InfrastructureException(f"Failed to reset ChromaDB collection: {e}") from e

    def _flatten_metadata(self, metadata: dict) -> dict:
        flattened = {}
        for key, value in metadata.items():
            if value is None:
                # ChromaDB often issues with None, skip or use empty string
                continue

            if isinstance(value, (dict, list)):
                # 복잡한 타입은 JSON 문자열로 직렬화
                flattened[f"{key}_json"] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                # Primitive 타입은 그대로 유지
                flattened[key] = value
            else:
                # ChromaDB가 지원하지 않는 타입은 문자열로 변환하여 저장 (Robustness)
                try:
                    flattened[key] = str(value)
                except Exception:
                    pass
        return flattened

    def save(self, document: Document) -> None:
        try:
            # Document Metadata Flattening
            meta_dict = (
                document.metadata.model_dump() if hasattr(document.metadata, "model_dump") else document.metadata
            )
            flattened_metadata = self._flatten_metadata(meta_dict)

            # source_url handling if explicit parameter is needed, but mostly it's in metadata
            # Ensure mandatory fields or fallbacks if needed?
            # Chroma allows arbitrary metadata.

            self.collection.add(documents=[document.content], metadatas=[flattened_metadata], ids=[str(document.id)])
        except Exception as e:
            logger.error(f"Failed to save document to ChromaDB: {e}")
            raise InfrastructureException(f"Failed to save document to ChromaDB: {e}") from e

    def save_with_chunks(self, document: Document, chunks: list[Chunk]) -> None:
        """DocumentRepository 인터페이스 구현: 문서와 청크 저장"""
        # ChromaDB는 Chunk만 저장하면 됨 (Embedding 검색용)
        # 문서는 필요 시 저장하거나 생략 가능. 현재 정책은 Chunk Store.
        self.save_chunks(chunks)

    def save_chunks(self, chunks: list[Chunk]) -> None:
        """청크 리스트를 저장합니다 (Embedding은 chunk.content 기준)
        [Spec 037] Gemini API Rate Limit 대응을 위한 재시도 로직 추가
        """
        import random
        import time

        # Prepare data for all chunks
        all_ids = [str(chunk.id) for chunk in chunks]
        all_documents = [chunk.content for chunk in chunks]
        all_metadatas = []

        for chunk in chunks:
            meta = self._flatten_metadata(chunk.metadata)
            meta["parent_id"] = str(chunk.parent_id)
            meta["index"] = chunk.index
            # ChromaDB often issues with None, ensure parent_id is string
            all_metadatas.append(meta)

        total_chunks = len(chunks)
        if total_chunks == 0:
            return

        # Process in batches
        for i in range(0, total_chunks, self.batch_size):
            batch_ids = all_ids[i : i + self.batch_size]
            batch_documents = all_documents[i : i + self.batch_size]
            batch_metas = all_metadatas[i : i + self.batch_size]

            current_batch_count = (i // self.batch_size) + 1
            total_batches = (total_chunks + self.batch_size - 1) // self.batch_size

            logger.info(f"Saving batch {current_batch_count}/{total_batches} ({len(batch_ids)} chunks)...")

            max_retries = 5
            base_delay = 2  # seconds

            for attempt in range(max_retries):
                try:
                    self.collection.add(ids=batch_ids, documents=batch_documents, metadatas=batch_metas)
                    break  # Batch Success, move to next batch
                except Exception as e:
                    # 429 (Rate Limit) or other errors
                    error_msg = str(e).lower()
                    is_rate_limit = "429" in error_msg or "quota" in error_msg
                    is_ssl_error = "ssl" in error_msg or "eof" in error_msg

                    if attempt < max_retries - 1 and (is_rate_limit or "retry" in error_msg or is_ssl_error):
                        delay = (base_delay**attempt) + random.uniform(0, 1)
                        logger.warning(
                            f"ChromaDB batch save failed (attempt {attempt + 1}/{max_retries}). Retrying in {delay:.2f}s... Error: {e}"
                        )
                        time.sleep(delay)
                        continue

                    logger.error(f"Failed to save batch to ChromaDB after {max_retries} attempts: {e}")
                    raise InfrastructureException(f"Failed to save chunks batch to ChromaDB: {e}") from e

    def get(self, doc_id: UUID) -> Document | None:
        try:
            # ChromaDB는 주된 검색 용도가 아니므로 최소 구현
            # Neo4j가 primary source
            result = self.collection.get(ids=[str(doc_id)])

            # Robust Null Check
            if not result:
                return None

            documents = result.get("documents")
            if not documents or len(documents) == 0:
                return None

            metadatas = result.get("metadatas")
            if not metadatas or len(metadatas) == 0:
                return None

            # ChromaDB에서 객체 재구성은 손실이 발생함 (full metadata 없음)
            # 하지만 기본 매핑은 구현
            return Document(
                id=str(doc_id),  # str expected
                content=documents[0],
                # source_url removed from constructor
                metadata=metadatas[0],
            )
        except Exception as e:
            # 조회 실패는 Logging 후 None 반환 (서비스 중단 방지)
            logger.warning(f"Failed to get document from ChromaDB (id={doc_id}): {e}")
            return None

    def list_documents(self, limit: int = 10, search_term: str | None = None) -> list[Document]:
        try:
            # ChromaDB peek (샘플 조회)
            result = self.collection.peek(limit=limit)
            docs: list[Document] = []
            if result and result["ids"]:
                for i in range(len(result["ids"])):
                    docs.append(
                        Document(
                            id=result["ids"][i],  # str
                            content=result["documents"][i],
                            metadata=result["metadatas"][i],
                        )
                    )
            return docs
        except Exception as e:
            logger.error(f"Failed to list documents from ChromaDB: {e}")
            raise InfrastructureException(f"Failed to list documents from ChromaDB: {e}") from e

    def get_chunks(self, doc_id: UUID) -> list[Chunk]:
        """Retrieve all chunks for a document from Chroma."""
        try:
            # use where filter on metadata
            result = self.collection.get(where={"parent_id": str(doc_id)})
            chunks = []
            if result and result["ids"]:
                for i in range(len(result["ids"])):
                    chunk_id = result["ids"][i]
                    content = result["documents"][i]
                    metadata = result["metadatas"][i]
                    chunks.append(
                        Chunk(
                            id=UUID(chunk_id),
                            content=content,
                            metadata=metadata,
                            parent_id=UUID(metadata.get("parent_id")) if metadata.get("parent_id") else str(doc_id),
                            index=int(metadata.get("index", 0)),
                        )
                    )
            # Sort by index
            chunks.sort(key=lambda x: x.index)
            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks from ChromaDB: {e}")
            return []

    def _build_where_clause(self, filters: dict | None) -> dict | None:
        """
        Build ChromaDB where clause from filters.
        Supports single value equality and list value inclusion ($in).
        """
        if not filters:
            return None

        conditions = []
        for key, value in filters.items():
            # Map 'doc_id' -> 'parent_id' for chunk
            target_key = "parent_id" if key == "doc_id" else key

            if isinstance(value, list):
                if len(value) == 1:
                    conditions.append({target_key: value[0]})
                elif len(value) > 1:
                    conditions.append({target_key: {"$in": value}})
            else:
                conditions.append({target_key: value})

        if not conditions:
            return None

        if len(conditions) == 1:
            return conditions[0]
        else:
            # ChromaDB supports implicit AND structure?
            # Yes, standard Chroma where clause is a dict.
            merged_where = {}
            for cond in conditions:
                merged_where.update(cond)
            # Note: If keys collide (same key used twice for AND??), this dict update overwrites.
            # But here keys are unique (iterating filters.items).
            return merged_where

    def search(self, query: str, limit: int = 5, filters: dict | None = None) -> list[Chunk]:
        """Vector search implementation."""
        try:
            where_clause = self._build_where_clause(filters)
            results = self.collection.query(query_texts=[query], n_results=limit, where=where_clause)

            chunks = []
            if results and results["ids"] and results["ids"][0]:
                logger.info(
                    f"Chroma Search results: found {len(results['ids'][0])} candidates. Top IDs: {results['ids'][0][:3]}"
                )
                for i in range(len(results["ids"][0])):
                    chunk_id = results["ids"][0][i]
                    content = results["documents"][0][i]
                    metadata = results["metadatas"][0][i]

                    chunks.append(
                        Chunk(
                            id=UUID(chunk_id),
                            content=content,
                            metadata=metadata,
                            parent_id=UUID(metadata.get("parent_id")) if metadata.get("parent_id") else None,
                            index=int(metadata.get("index", 0)),
                        )
                    )
            return chunks
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []

    def search_mmr(
        self, query: str, limit: int = 5, diversity: float = 0.5, filters: dict | None = None
    ) -> list[Chunk]:
        """
        Maximal Marginal Relevance (MMR) Search.
        diversity: 0.0 (Pure Relevance) ~ 1.0 (Pure Diversity).
        """
        try:
            import numpy as np
        except ImportError:
            logger.error("MMR search requires numpy.")
            return self.search(query, limit, filters=filters)

        try:
            # 1. Fetch Candidates
            fetch_k = min(limit * 20, 100)
            where_clause = self._build_where_clause(filters)

            results = self.collection.query(
                query_texts=[query],
                n_results=fetch_k,
                include=["metadatas", "documents", "embeddings", "distances"],
                where=where_clause,
            )

            if not results or not results["ids"] or len(results["ids"][0]) == 0:
                logger.warning(f"Chroma MMR: No candidates found for query: {query}")
                return []

            logger.info(
                f"Chroma MMR candidates: found {len(results['ids'][0])} candidates. Top IDs: {results['ids'][0][:3]}"
            )
            candidate_ids = results["ids"][0]
            candidate_docs = results["documents"][0]
            candidate_metas = results["metadatas"][0]
            candidate_embeddings = np.array(results["embeddings"][0])

            # 2. Embed Query
            query_embedding = np.array(self.collection._embedding_function([query]))
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)  # (1, D)

            # Helper: Cosine Similarity
            def compute_similarity(v1, v2):
                # v1: (N, D), v2: (M, D) -> (N, M)
                norm_v1 = np.linalg.norm(v1, axis=1, keepdims=True)
                norm_v2 = np.linalg.norm(v2, axis=1, keepdims=True)

                # Avoid division by zero
                norm_v1[norm_v1 == 0] = 1e-10
                norm_v2[norm_v2 == 0] = 1e-10

                dot = np.dot(v1, v2.T)
                return dot / (norm_v1 @ norm_v2.T)

            # 3. Calculate Query Similarity
            # query_embedding: (1, D), candidate_embeddings: (K, D)
            # Returns (1, K) -> flatten to (K,)
            query_sim_matrix = compute_similarity(query_embedding, candidate_embeddings)
            query_similitudes = query_sim_matrix[0]

            # 4. MMR Loop
            selected_indices = []
            candidate_indices = list(range(len(candidate_ids)))
            lambda_mult = 1.0 - diversity

            for _ in range(min(limit, len(candidate_ids))):
                best_mmr = -float("inf")
                best_idx = -1

                for idx in candidate_indices:
                    if idx in selected_indices:
                        continue

                    relevance = query_similitudes[idx]

                    if not selected_indices:
                        redundancy = 0.0
                    else:
                        current_vec = candidate_embeddings[idx].reshape(1, -1)
                        selected_vecs = candidate_embeddings[selected_indices]
                        # Sim(Current, Selected) -> (1, S)
                        sim_to_selected = compute_similarity(current_vec, selected_vecs)
                        redundancy = np.max(sim_to_selected)

                    mmr_score = (lambda_mult * relevance) - ((1 - lambda_mult) * redundancy)

                    if mmr_score > best_mmr:
                        best_mmr = mmr_score
                        best_idx = idx

                if best_idx != -1:
                    selected_indices.append(best_idx)

            mmr_chunks = []
            for idx in selected_indices:
                meta = candidate_metas[idx]
                chunk_id = candidate_ids[idx]
                content = candidate_docs[idx]

                mmr_chunks.append(
                    Chunk(
                        id=UUID(chunk_id),
                        content=content,
                        metadata=meta,
                        parent_id=UUID(meta.get("parent_id")) if meta.get("parent_id") else None,
                        index=int(meta.get("index", 0)),
                    )
                )
            return mmr_chunks

        except Exception as e:
            logger.error(f"MMR search logic failed: {e}")
            return self.search(query, limit, filters=filters)

    def get_all_chunk_ids(self) -> set[str]:
        """ChromaDB의 모든 청크 ID를 가져옵니다."""
        try:
            # include=[] means only IDs are returned, which is efficient
            result = self.collection.get(include=[])
            return set(result["ids"])
        except Exception as e:
            logger.error(f"Failed to get all chunk IDs from ChromaDB: {e}")
            return set()

    def get_document_stats(self) -> list[dict]:
        """ChromaDB의 문서별 통계 (Chroma는 Chunk 중심이므로 기본 정보만 반환)"""
        try:
            # Chroma에서 중복되지 않는 parent_id 목록을 가져오는 효율적인 방법이 제한적이므로
            # 전체 가져온 후 그룹화 (Chroma는 서브 저장소이므로 빈도 낮음)
            result = self.collection.get(include=["metadatas"])
            if not result or not result["metadatas"]:
                return []
            stats_map = {}
            for meta in result["metadatas"]:
                pid = meta.get("parent_id")
                if not pid:
                    continue
                if pid not in stats_map:
                    stats_map[pid] = {"id": pid, "title": meta.get("title", "Untitled"), "chunk_count": 0}
                stats_map[pid]["chunk_count"] += 1
            return list(stats_map.values())
        except Exception as e:
            logger.error(f"Failed to get document stats from ChromaDB: {e}")
            return []

    def get_all_chunk_metadata(self) -> list[dict]:
        """ChromaDB의 모든 청크 핵심 메타데이터를 일괄 조회합니다."""
        try:
            result = self.collection.get(include=["metadatas"])
            if not result or not result["ids"]:
                return []
            return [
                {"id": result["ids"][i], "parent_id": result["metadatas"][i].get("parent_id")}
                for i in range(len(result["ids"]))
            ]
        except Exception as e:
            logger.error(f"Failed to get all chunk metadata from ChromaDB: {e}")
            return []

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[Chunk]:
        """여러 청크 ID에 해당하는 청크들을 한 번에 가져옵니다."""
        try:
            result = self.collection.get(ids=chunk_ids)
            chunks = []
            if result and result["ids"]:
                for i in range(len(result["ids"])):
                    chunk_id = result["ids"][i]
                    content = result["documents"][i]
                    metadata = result["metadatas"][i]
                    chunks.append(
                        Chunk(
                            id=chunk_id,
                            content=content,
                            metadata=metadata,
                            parent_id=metadata.get("parent_id"),
                            index=int(metadata.get("index", 0)),
                        )
                    )
            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks by IDs from ChromaDB: {e}")
            return []
