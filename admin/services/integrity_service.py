from app.domain.services.storage_integrity_service import StorageIntegrityService
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.interfaces.api.dependencies import get_neo4j_driver

class IntegrityAdminService:
    def __init__(self):
        self.driver = get_neo4j_driver()
        self.primary_repo = Neo4jStorage(self.driver)
        self.target_repo = ChromaStorage()
        self.service = StorageIntegrityService(self.primary_repo, self.target_repo)

    def get_stats(self):
        return self.service.get_drift_report()

    def get_document_reports(self):
        return self.service.get_document_drift_report()

    def get_missing_chunk_sample(self, doc_id: str):
        return self.service.get_missing_chunk_sample(doc_id)

    async def get_cleaned_context(self, doc_id: str):
        return await self.service.get_cleaned_context(doc_id)

    async def enrich_knowledge_graph(self, doc_id: str):
        from app.interfaces.api.dependencies import get_semantic_extractor, get_checkpointer
        import asyncio
        
        # FastAPI dependency injection outside of FastAPI context
        cp = await get_checkpointer()
        extractor = await get_semantic_extractor(cp)
        return await self.service.enrich_knowledge_graph(doc_id, extractor)

    def sync_document(self, doc_id: str):
        return self.service.sync_document(doc_id)

    def sync_all(self, callback=None):
        return self.service.sync_all(callback=callback)

    def close(self):
        self.driver.close()
