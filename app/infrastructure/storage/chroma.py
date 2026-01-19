import json
import os
from uuid import UUID
from typing import List

import chromadb
from chromadb.utils import embedding_functions
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.exceptions import InfrastructureException
from app.core.logging_config import setup_logger
from app.domain.entities.document import Document
from app.domain.entities.chunk import Chunk
from app.domain.interfaces.document_repository import DocumentRepository

logger = setup_logger(__name__)

class ChromaStorage(DocumentRepository):
    def __init__(self):
        host = os.getenv("CHROMA_HOST", "localhost")
        port = os.getenv("CHROMA_PORT", "8001")
        self.client = chromadb.HttpClient(host=host, port=int(port))

        # Gemini Embedding API 설정
        gemini_api_key = os.getenv("GEMINI_API_KEY")
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

        self.collection = self.client.get_or_create_collection(name="documents", embedding_function=gemini_ef)

    def _flatten_metadata(self, metadata: dict) -> dict:
        flattened = {}
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                # 복잡한 타입은 JSON 문자열로 직렬화
                flattened[f"{key}_json"] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool, type(None))):
                # Primitive 타입은 그대로 유지
                flattened[key] = value
            # ChromaDB가 지원하지 않는 타입은 스킵
        return flattened

    def save(self, document: Document) -> None:
        try:
            # Document Metadata Flattening
            flattened_metadata = self._flatten_metadata(document.metadata)
            
            # source_url handling if explicit parameter is needed, but mostly it's in metadata
            # Ensure mandatory fields or fallbacks if needed? 
            # Chroma allows arbitrary metadata.

            self.collection.add(
                documents=[document.content], 
                metadatas=[flattened_metadata], 
                ids=[str(document.id)]
            )
        except Exception as e:
            logger.error(f"Failed to save document to ChromaDB: {e}")
            raise InfrastructureException(f"Failed to save document to ChromaDB: {e}") from e

    def save_chunks(self, chunks: List[Chunk]) -> None:
        """청크 리스트를 저장합니다 (Embedding은 chunk.content 기준)"""
        try:
            ids = [chunk.id for chunk in chunks]
            documents = [chunk.content for chunk in chunks]
            
            metadatas = []
            for chunk in chunks:
                meta = self._flatten_metadata(chunk.metadata)
                meta["parent_id"] = chunk.parent_id
                meta["index"] = chunk.index
                metadatas.append(meta)
                
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        except Exception as e:
            logger.error(f"Failed to save chunks to ChromaDB: {e}")
            raise InfrastructureException(f"Failed to save chunks to ChromaDB: {e}") from e

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
                id=str(doc_id), # str expected
                content=documents[0],
                # source_url removed from constructor
                metadata=metadatas[0],
            )
        except Exception as e:
            # 조회 실패는 Logging 후 None 반환 (서비스 중단 방지)
            logger.warning(f"Failed to get document from ChromaDB (id={doc_id}): {e}")
            return None

    def list_documents(self, limit: int = 10) -> list[Document]:
        try:
            # ChromaDB peek (샘플 조회)
            result = self.collection.peek(limit=limit)
            docs: list[Document] = []
            if result and result["ids"]:
                for i in range(len(result["ids"])):
                    docs.append(
                        Document(
                            id=result["ids"][i], # str
                            content=result["documents"][i],
                            metadata=result["metadatas"][i],
                        )
                    )
            return docs
        except Exception as e:
            logger.error(f"Failed to list documents from ChromaDB: {e}")
            raise InfrastructureException(f"Failed to list documents from ChromaDB: {e}") from e
