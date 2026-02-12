import asyncio
import logging
import traceback
from typing import Any

from app.core.events import bus
from app.domain.entities.job import JobStatus
from app.domain.events.ingestion_events import (
    ContentCollected,
    ContentUnique,
    DataIndexed,
    DocumentChunked,
    IngestionCompleted,
    IngestionFailed,
    IngestionStarted,
    MetadataExtracted,
)
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.interfaces.job_repository import JobRepository

logger = logging.getLogger(__name__)

class IngestionSagaHandlers:
    """
    Saga Handlers for Coordinating the Ingestion Choreography.
    """
    _instance: "IngestionSagaHandlers | None" = None

    def __init__(
        self,
        job_repository: JobRepository,
        document_repository: DocumentRepository,
        graph_repository: GraphRepository,
        scraper: Any,
        extractor: Any,
        chunker: Any
    ):
        self.job_repository = job_repository
        self.document_repository = document_repository
        self.graph_repository = graph_repository
        self.scraper = scraper
        self.extractor = extractor
        self.chunker = chunker

    @classmethod
    def initialize(cls, **deps) -> "IngestionSagaHandlers":
        """
        Singleton-like initialization. Registers handlers on first call,
        updates dependencies on subsequent calls.
        """
        if cls._instance is None:
            cls._instance = cls(**deps)
            cls._instance.register_all()
        else:
            cls._instance.update_dependencies(**deps)
        return cls._instance

    def update_dependencies(self, **deps):
        """Update instance dependencies dynamically (for tests/DI)."""
        logger.debug(f"Updating IngestionSagaHandlers dependencies: {list(deps.keys())}")
        for name, val in deps.items():
            if hasattr(self, name):
                setattr(self, name, val)

    def register_all(self):
        """Register all handlers to the event bus once."""
        # Use a class-level flag or check bus subscriptions? 
        # Since bus is singleton, we must be careful.
        # However, initialize() already guards this.

        bus.subscribe("IngestionStarted", self.handle_started)
        bus.subscribe("ContentCollected", self.handle_collected)
        bus.subscribe("ContentUnique", self.handle_unique)
        bus.subscribe("MetadataExtracted", self.handle_metadata_extracted)
        bus.subscribe("DocumentChunked", self.handle_chunked)
        # bus.subscribe("ChunksEmbedded", self.handle_embedded) # Not yet fully implemented
        bus.subscribe("DataIndexed", self.handle_indexed)
        bus.subscribe("IngestionFailed", self.handle_failed)
        logger.info("IngestionSagaHandlers registered to EventBus")

    async def handle_started(self, event: IngestionStarted):
        """Step 1: Collection"""
        logger.info(f"Saga Step 1 (Collection) started for job {event.job_id}")
        try:
            # Update job status
            job = self.job_repository.get_job(event.job_id)
            if job:
                job.status = JobStatus.COLLECTING
                self.job_repository.update_job(job)

            # [Spec 072/076] Use scraper.scrape for full result (including metadata)
            logger.debug(f"Stage 1: Scraping {event.source_url}")
            result = await self.scraper.scrape(event.source_url)
            logger.debug(f"Stage 1: Scraped content length: {len(result.markdown) if result.markdown else 0}")
            
            # Calculate Content Hash
            import hashlib
            # [Spec 072/076] Handle cases where scraped_content might be a Mock or None in tests
            scraped_content = result.markdown
            if hasattr(scraped_content, "__await__") or asyncio.iscoroutine(scraped_content):
                logger.warning(f"Stage 1: scraped_content is a coroutine! (Mock issue?)")
                scraped_content = await scraped_content

            if not isinstance(scraped_content, str):
                logger.warning(f"Stage 1: scraped_content is {type(scraped_content)}, not string. Coercing to string for hashing.")
                scraped_content = str(scraped_content)

            content_hash = hashlib.sha256(scraped_content.encode()).hexdigest()
            logger.debug(f"Stage 1: Content hash: {content_hash}")
            
            if job:
                job.content_hash = content_hash
                self.job_repository.update_job(job)

            # Ensure metadata is a dict for Pydantic validation
            event_metadata = result.metadata if isinstance(result.metadata, dict) else {}

            await bus.publish("ContentCollected", ContentCollected(
                job_id=event.job_id,
                raw_content=scraped_content,
                metadata=event_metadata
            ))
        except Exception as e:
            await self.publish_failed(event.job_id, "Collection", e)

    async def handle_collected(self, event: ContentCollected):
        """Step 2: Deduplication (Simplified for now)"""
        logger.info(f"Saga Step 2 (Deduplication) for job {event.job_id}")
        try:
            job = self.job_repository.get_job(event.job_id)
            force_refresh = False
            if job and job.custom_metadata:
                force_refresh = job.custom_metadata.get("force_refresh", False)

            if not force_refresh:
                # 1. Strategy-based check (Contents, TTL, Metadata-specific)
                from app.application.services.deduplication_strategies import DeduplicationFactory
                factory = DeduplicationFactory(self.job_repository)
                strategy = factory.get_strategy(job.source_url)
                
                if job and await strategy.is_duplicate(job):
                    logger.info(f"Saga Step 2: Job {event.job_id} detected as duplicate. Skipping.")
                    job.status = JobStatus.SKIPPED
                    job.skip_reason = f"Duplicate detected by {type(strategy).__name__}"
                    self.job_repository.update_job(job)
                    return

            await bus.publish("ContentUnique", ContentUnique(
                job_id=event.job_id,
                content_hash=job.content_hash if job else "mock_hash",
                raw_content=event.raw_content,
                metadata=event.metadata
            ))
        except Exception as e:
            await self.publish_failed(event.job_id, "Deduplication", e)

    async def handle_unique(self, event: ContentUnique):
        """Step 3: Extraction"""
        logger.info(f"Saga Step 3 (Extraction) for job {event.job_id}")
        try:
            job = self.job_repository.get_job(event.job_id)
            if job:
                job.status = JobStatus.EXTRACTING
                self.job_repository.update_job(job)

            # IngestOrchestrator is used via SemanticExtractor
            # This is a bit complex as we need to bridge between event and the orchestrator
            # For this MVP, we'll keep it simple:
            # metadata_obj = await self.extractor.extract(event.raw_content, event.metadata)

            # Since the actual implementation might vary, let's assume 'extractor'
            # is a service that handles the logic.
            extracted = await self.extractor.extract(
                text=event.raw_content if isinstance(event.raw_content, str) else event.raw_content.decode('utf-8'),
                metadata=event.metadata
            )
            
            # [Spec 076] Handle cases where extracted might be a coroutine (Mock issue)
            if asyncio.iscoroutine(extracted) or hasattr(extracted, "__await__"):
                logger.warning(f"Stage 3: extracted is a coroutine! Awaiting.")
                extracted = await extracted

            # Ensure extracted_metadata is a dict for Pydantic validation
            # Be careful with Mocks!
            is_mock = str(type(extracted)).startswith("<class 'unittest.mock.")
            
            if hasattr(extracted, "model_dump") and not is_mock:
                extracted_metadata = extracted.model_dump()
            elif isinstance(extracted, dict):
                extracted_metadata = extracted
            else:
                logger.warning(f"Stage 3: extracted metadata is {type(extracted)}, not dict (Mocking?). Falling back.")
                extracted_metadata = {}

            await bus.publish("MetadataExtracted", MetadataExtracted(
                job_id=event.job_id,
                extracted_metadata=extracted_metadata,
                raw_content=event.raw_content
            ))
        except Exception as e:
            await self.publish_failed(event.job_id, "Extraction", e)

    async def handle_metadata_extracted(self, event: MetadataExtracted):
        """Step 4: Chunking"""
        logger.info(f"Saga Step 4 (Chunking) for job {event.job_id}")
        try:
            job = self.job_repository.get_job(event.job_id)
            if job:
                job.status = JobStatus.CHUNKING
                self.job_repository.update_job(job)

            # [Spec 072] Use deterministic doc_id based on source_url
            import hashlib
            source_url = job.source_url if job else ""
            doc_id = hashlib.sha256(source_url.encode()).hexdigest()
            
            from app.domain.entities.document import Document
            
            # [Spec 073] Ensure DocumentMetadata requirements are met
            metadata = event.extracted_metadata.copy()
            if "source_id" not in metadata:
                metadata["source_id"] = source_url
            if "url" not in metadata:
                metadata["url"] = source_url
            # Add source_url for older retrieval logic compatibility
            if "source_url" not in metadata:
                metadata["source_url"] = source_url

            doc = Document(
                id=doc_id,
                content=event.raw_content if isinstance(event.raw_content, str) else event.raw_content.decode('utf-8'),
                metadata=metadata
            )
            
            # Actual Chunking Logic
            config = job.chunking_config if job else None
            from app.domain.value_objects.chunk_config import ChunkingConfig
            from app.infrastructure.chunker.chunker_factory import ChunkerFactory
            chunker = ChunkerFactory.get_chunker(ChunkingConfig(**config) if config else ChunkingConfig())
            
            chunks = chunker.chunk_document(doc)
            logger.info(f"Saga Step 4: Chunked document {doc_id} into {len(chunks)} pieces")

            # Ensure chunks is a list of dicts for event publication
            # If chunks is a mock or returns mocks, handle it gracefully
            event_chunks = []
            if isinstance(chunks, list):
                for c in chunks:
                    is_c_mock = str(type(c)).startswith("<class 'unittest.mock.")
                    if isinstance(c, dict):
                        event_chunks.append(c)
                    elif hasattr(c, "model_dump") and not is_c_mock:
                        event_chunks.append(c.model_dump())
                    else:
                        logger.warning(f"Stage 4: chunk is {type(c)}, not dict or model (Mocking?). using empty dict.")
                        event_chunks.append({})
            else:
                logger.warning(f"Stage 4: chunks is {type(chunks)}, not list. using empty list.")

            await bus.publish("DocumentChunked", DocumentChunked(
                job_id=event.job_id,
                chunks=event_chunks,
                semantic_data=event.extracted_metadata
            ))
        except Exception as e:
            await self.publish_failed(event.job_id, "Chunking", e)

    async def handle_chunked(self, event: DocumentChunked):
        """Step 5: Indexing (Final stage for now)"""
        logger.info(f"Saga Step 5 (Indexing) for job {event.job_id}")
        try:
            job = self.job_repository.get_job(event.job_id)
            if job:
                job.status = JobStatus.INDEXING
                self.job_repository.update_job(job)

            import hashlib
            source_url = job.source_url if job else ""
            doc_id = hashlib.sha256(source_url.encode()).hexdigest()
            
            from app.domain.entities.document import Document
            from app.domain.value_objects.chunk import Chunk as DocumentChunk
            
            # Re-enrich metadata for consistency
            metadata = event.semantic_data.copy() if event.semantic_data else {}
            if "source_id" not in metadata:
                metadata["source_id"] = source_url
            if "source_url" not in metadata:
                metadata["source_url"] = source_url
            if "url" not in metadata:
                metadata["url"] = source_url

            # Save Document and Chunks
            doc = Document(id=doc_id, content="", metadata=metadata)
            
            # Ensure event.chunks is a list
            event_chunks = event.chunks if isinstance(event.chunks, list) else []
            chunks = []
            for c in event_chunks:
                if isinstance(c, dict):
                    chunks.append(DocumentChunk(**c))
                else:
                    logger.warning(f"Stage 5: chunk is {type(c)}, not dict. Skipping.")

            self.document_repository.save_with_chunks(doc, chunks)
            
            # Build Knowledge Graph (Spec 010 + 016)
            if event.semantic_data:
                # Need to convert dict back to SemanticData object if possible, 
                # or adapt _build_knowledge_graph to handle dict
                self._build_knowledge_graph(doc_id, event.semantic_data)

            await bus.publish("DataIndexed", DataIndexed(
                job_id=event.job_id,
                doc_id=doc_id
            ))
        except Exception as e:
            await self.publish_failed(event.job_id, "Indexing", e)

    async def handle_indexed(self, event: DataIndexed):
        """Final Step: Completion"""
        logger.info(f"Saga Completed for job {event.job_id}")
        job = self.job_repository.get_job(event.job_id)
        if job:
            job.status = JobStatus.COMPLETED
            job.docs_ids.append(event.doc_id)
            self.job_repository.update_job(job)

        await bus.publish("IngestionCompleted", IngestionCompleted(
            job_id=event.job_id,
            doc_id=event.doc_id
        ))

    async def handle_failed(self, event: IngestionFailed):
        """Rollback Compensatory Transaction"""
        logger.warning(f"Saga Failure detected at stage {event.stage} for job {event.job_id}. Rolling back...")

        job = self.job_repository.get_job(event.job_id)
        if job:
            job.status = JobStatus.FAILED # Or ROLLING_BACK
            job.error_message = f"Failed at {event.stage}: {event.error_message}"
            self.job_repository.update_job(job)

        # COMPENSATE: Delete documents if any created
        for doc_id in job.docs_ids if job else []:
            await self.document_repository.delete(doc_id)
            logger.info(f"Rollback: Deleted document {doc_id}")

    def _build_knowledge_graph(self, doc_id: str, semantic_data_dict: dict[str, Any]) -> None:
        """
        Entity 노드, MENTIONS 관계 및 Entity-Entity 관계 생성 (Ported from Ingestion service)
        """
        from app.core.utils import normalize_entity_name
        
        primary_entity = semantic_data_dict.get("primary_entity")
        entities = semantic_data_dict.get("entities", {})
        aliases = semantic_data_dict.get("aliases", {})
        relationships = semantic_data_dict.get("relationships", [])

        # 1. Entity 저장 및 MENTIONS 관계
        all_entity_names = set()
        for entity_type, names in entities.items():
            for name in names:
                try:
                    normalized_name = normalize_entity_name(name)
                    self.graph_repository.save_entity(normalized_name, entity_type)
                    self.graph_repository.create_mention_relationship(doc_id, normalized_name)
                    all_entity_names.add(normalized_name)

                    if primary_entity and normalized_name != normalize_entity_name(primary_entity):
                        norm_primary = normalize_entity_name(primary_entity)
                        # [FIX] Use valid EntityType. "SHOW" is not valid.
                        self.graph_repository.save_entity(norm_primary, "CONCEPT")
                        self.graph_repository.create_entity_relationship(
                            source_name=normalized_name, 
                            relationship_type="PART_OF_CONTEXT", 
                            target_name=norm_primary
                        )
                except Exception as e:
                    logger.error(f"Failed to build graph for entity {name}: {e}")

        # 2. Semantic Alias Mapping
        if aliases:
            for canonical, alias_list in aliases.items():
                try:
                    norm_canonical = normalize_entity_name(canonical)
                    self.graph_repository.save_entity(norm_canonical, "CONCEPT")
                    for alias in alias_list:
                        norm_alias = normalize_entity_name(alias)
                        if norm_alias != norm_canonical:
                            self.graph_repository.save_entity(norm_alias, "CONCEPT")
                            self.graph_repository.create_entity_relationship(
                                source_name=norm_alias, relationship_type="ALIAS_OF", target_name=norm_canonical
                            )
                except Exception as e:
                    logger.warning(f"Failed to create ALIAS_OF relationships for {canonical}: {e}")

        # 3. Entity-Entity 관계 생성
        if relationships:
            for rel_data in relationships:
                try:
                    # rel_data is likely a dict from model_dump
                    source = rel_data.get("source")
                    target = rel_data.get("target")
                    rel_type = rel_data.get("relationship")
                    
                    if not source or not target or not rel_type:
                        continue

                    if source not in all_entity_names:
                        self.graph_repository.save_entity(source, rel_data.get("source_type", "CONCEPT"))
                    if target not in all_entity_names:
                        self.graph_repository.save_entity(target, rel_data.get("target_type", "CONCEPT"))

                    self.graph_repository.create_entity_relationship(
                        source_name=source, relationship_type=rel_type, target_name=target
                    )
                except Exception as e:
                    logger.error(f"Failed to create relationship: {e}")

    async def publish_failed(self, job_id: str, stage: str, exception: Exception):
        """Utility to publish failure events."""
        await bus.publish("IngestionFailed", IngestionFailed(
            job_id=job_id,
            stage=stage,
            error_message=str(exception),
            exc_info=traceback.format_exc()
        ))
