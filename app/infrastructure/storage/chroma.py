import json
import os
from uuid import UUID

import chromadb
from chromadb.utils import embedding_functions
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository


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
            model="models/text-embedding-004",
            google_api_key=gemini_api_key
        )
        
        # ChromaDB가 요구하는 embedding function 형식으로 래핑
        class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
            def __call__(self, input: list[str]) -> list[list[float]]:
                # LangChain의 embed_documents 메서드 사용
                return langchain_embeddings.embed_documents(input)
        
        gemini_ef = GeminiEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="documents",
            embedding_function=gemini_ef
        )

    def save(self, document: AtomicDocument) -> None:
        # ChromaDB 제약사항: metadata 값으로 str, int, float, bool만 허용
        # 복잡한 타입은 JSON 문자열로 직렬화하여 저장
        flattened_metadata = {"source_url": document.source_url}

        for key, value in document.metadata.items():
            if isinstance(value, (dict, list)):
                # 복잡한 타입은 JSON 문자열로 직렬화
                flattened_metadata[f"{key}_json"] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool, type(None))):
                # Primitive 타입은 그대로 유지
                flattened_metadata[key] = value
            # ChromaDB가 지원하지 않는 타입은 스킵

        self.collection.add(
            documents=[document.content],
            metadatas=[flattened_metadata],
            ids=[str(document.id)]
        )

    def get(self, doc_id: UUID) -> AtomicDocument | None:
        # ChromaDB는 주된 검색 용도가 아니므로 최소 구현
        # Neo4j가 primary source
        result = self.collection.get(ids=[str(doc_id)])
        if result and result['documents']:
             # ChromaDB에서 객체 재구성은 손실이 발생함 (full metadata 없음)
             # 하지만 기본 매핑은 구현
             return AtomicDocument(
                 id=doc_id,
                 content=result['documents'][0],
                 source_url=result['metadatas'][0].get("source_url", ""),
                 metadata=result['metadatas'][0]
             )
        return None

    def list_documents(self, limit: int = 10) -> list[AtomicDocument]:
        # ChromaDB peek (샘플 조회)
        result = self.collection.peek(limit=limit)
        docs: list[AtomicDocument] = []
        if result and result['ids']:
            for i in range(len(result['ids'])):
                 docs.append(AtomicDocument(
                     id=UUID(result['ids'][i]),
                     content=result['documents'][i],
                     source_url=result['metadatas'][i].get("source_url", ""),
                     metadata=result['metadatas'][i]
                 ))
        return docs
