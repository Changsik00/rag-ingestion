import asyncio
from datetime import datetime, timezone
from uuid import UUID

from app.application.interfaces.scraper import ScraperInterface
from app.application.services.deduplication_strategies import DeduplicationFactory
from app.application.services.semantic_extractor import SemanticExtractor
from app.core.exceptions import BaseAppError
from app.core.logger import setup_logger
from app.domain.entities.document import Document
from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.chunker import Chunker
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.interfaces.job_repository import JobRepository

logger = setup_logger(__name__)


class Ingestion:
    def __init__(
        self,
        scraper: ScraperInterface,
        repository: DocumentRepository,
        graph: GraphRepository,
        job_repository: JobRepository,
        chunker: Chunker | None = None,
        extractor: SemanticExtractor | None = None,
    ):
        self.scraper = scraper
        self.repository = repository
        self.graph = graph
        self.job_repository = job_repository
        self._chunker = chunker
        self.extractor = extractor
        self.deduplication_factory = DeduplicationFactory(job_repository)

        # [Spec 046] Inject LLM into Quality Checker if using CompositeScraper
        from app.infrastructure.scrapers.composite_scraper import CompositeScraper

        if isinstance(self.scraper, CompositeScraper) and self.extractor:
            self.scraper.quality_checker.llm = self.extractor.llm
            self.scraper.youtube_scraper.llm = self.extractor.llm

    def _get_chunker(self, config_dict: dict | None = None) -> Chunker:
        if self._chunker:
            return self._chunker

        from app.domain.value_objects.chunk_config import ChunkingConfig
        from app.infrastructure.chunker.chunker_factory import ChunkerFactory

        config = ChunkingConfig(**config_dict) if config_dict else ChunkingConfig()
        return ChunkerFactory.get_chunker(config)

    async def run(
        self,
        source: str,
        job_id: UUID,
        user_id: str | None = None,
        chunking_config: dict | None = None,
    ) -> list[str]:
        """인입 프로세스 실행"""
        try:
            # 1. 스크래핑
            logger.info(f"Starting scraping: {source}")
            content, metadata = await self.scraper.extract(source)

            # 2. 문서 엔티티 생성
            document = Document(content=content, metadata=metadata)

            # 3. 청킹
            chunker = self._get_chunker(chunking_config)
            document.chunks = chunker.chunk_document(document)
            logger.info(f"Document chunked into {len(document.chunks)} pieces using {type(chunker).__name__}")
            # 4. 저장
            self.repository.save_with_chunks(document, document.chunks)
            logger.info(f"Document saved with {len(document.chunks)} chunks")
            return [document.id]
        except Exception as e:
            logger.error(f"Failed to run ingestion: {e}")
            raise BaseAppError(f"Ingestion failed: {e}")

    def is_already_queued(
        self, url: str, custom_metadata: dict | None = None, content_hash: str | None = None
    ) -> IngestionJob | None:
        """
        Lightweight check to see if a job for this resource is already active/completed.
        Checks by URL first, then by hash, then by unique metadata (like video_id).
        """
        if not hasattr(self.job_repository, "find_last_job_by_source"):
            return None

        relevant_statuses = [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED]

        # 1. Check by exact URL
        last_job = self.job_repository.find_last_job_by_source(url, statuses=relevant_statuses)
        if last_job:
            return last_job

        # 2. Check by Content Hash
        if content_hash and hasattr(self.job_repository, "find_last_job_by_hash"):
            last_job = self.job_repository.find_last_job_by_hash(content_hash, statuses=relevant_statuses)
            if last_job:
                return last_job

        # 3. Check by Video ID (YouTube)
        if custom_metadata and "video_id" in custom_metadata:
            vid = custom_metadata["video_id"]
            if hasattr(self.job_repository, "find_last_job_by_metadata"):
                last_job = self.job_repository.find_last_job_by_metadata("video_id", vid, statuses=relevant_statuses)
                if last_job:
                    return last_job

        return None

    def create_job(
        self,
        url: str,
        retry_of: str | None = None,
        raw_content: bytes | None = None,
        filename: str | None = None,
        chunking_config: dict | None = None,
        custom_metadata: dict | None = None,
        content_hash: str | None = None,
    ) -> IngestionJob:
        """Create and persist a new job in PENDING state."""
        job = IngestionJob(
            source_url=url,
            status=JobStatus.PENDING,
            retry_of=retry_of,
            raw_content=raw_content,
            filename=filename,
            chunking_config=chunking_config,
            custom_metadata=custom_metadata,
            content_hash=content_hash,
        )
        self.job_repository.create_job(job)
        return job

    async def ingest_url(
        self,
        url: str,
        chunking_config: dict | None = None,
        custom_metadata: dict | None = None,
        force_refresh: bool = False,
    ) -> IngestionJob:
        """
        [Spec 076] Entry point for Saga-based ingestion.
        Publishes IngestionStarted event to the internal EventBus.
        """
        # [Spec 065] Initial ID/URL-based Deduplication Check
        if not force_refresh:
            from app.domain.entities.job import JobStatus
            last_job = self.job_repository.find_last_job_by_source(
                url,
                statuses=[JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING],
            )
            if last_job:
                logger.info(f"URL {url} already has an active or completed job: {last_job.job_id}")
                # We could return the existing job or create a SKIPPED one
                # For consistency with existing logic, let's created a SKIPPED job
                job = self.create_job(url=url, chunking_config=chunking_config, custom_metadata=custom_metadata)
                job.status = JobStatus.SKIPPED
                job.skip_reason = f"Duplicate of job {last_job.job_id} (Status: {last_job.status})"
                self.job_repository.update_job(job)
                return job

        # 1. Create Job Entry
        job = self.create_job(
            url=url, 
            chunking_config=chunking_config, 
            custom_metadata=custom_metadata
        )
        
        # [Spec 072/076] Store force_refresh in job for handlers to see
        if force_refresh:
             if job.custom_metadata is None:
                 job.custom_metadata = {}
             job.custom_metadata["force_refresh"] = True
             self.job_repository.update_job(job)

        # 2. Publish Event to start the Saga
        from app.core.events import bus
        from app.domain.events.ingestion_events import IngestionStarted
        
        # [Spec 076] Fire and forget: Decouple API response from Saga execution
        # Use asyncio.create_task to ensure the Saga starts in the background
        # but the current request returns immediately with the job ID.
        asyncio.create_task(bus.publish("IngestionStarted", IngestionStarted(
            job_id=job.job_id,
            source_url=url
        )))
        
        return job

    async def process_job(self, job_id: str, force_refresh: bool = False) -> None:
        """
        [Spec 076] Orchestrate the job processing using the Saga pattern.
        This replaces the old procedural logic to ensure transaction integrity.
        """
        job = self.job_repository.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} NOT FOUND in repository!")
            return

        try:
            from app.core.events import bus
            
            # [Spec 072/076] Store force_refresh in job for handlers to see
            if force_refresh:
                 if job.custom_metadata is None:
                     job.custom_metadata = {}
                 job.custom_metadata["force_refresh"] = True
                 self.job_repository.update_job(job)

            if job.raw_content:
                # Local file processing: Skip Step 1 (Collection) and jump to Step 2 (Deduplication)
                logger.info(f"Triggering Saga for local file: {job.filename} (Job {job_id})")
                from app.domain.events.ingestion_events import ContentCollected
                
                await bus.publish("ContentCollected", ContentCollected(
                    job_id=job.job_id,
                    raw_content=job.raw_content.decode("utf-8", errors="ignore") if isinstance(job.raw_content, bytes) else job.raw_content,
                    metadata=job.custom_metadata or {}
                ))
            else:
                # Web scraping: Start from Step 1 (Collection)
                logger.info(f"Triggering Saga for URL: {job.source_url} (Job {job_id})")
                from app.domain.events.ingestion_events import IngestionStarted
                
                await bus.publish("IngestionStarted", IngestionStarted(
                    job_id=job.job_id,
                    source_url=job.source_url
                ))

        except Exception as e:
            logger.exception(f"Failed to trigger Saga for job {job_id}")
            self._fail_job(job, f"Saga Trigger Error: {str(e)}")

    def _fail_job(self, job: IngestionJob, error_message: str) -> None:
        """Helper to mark job as failed."""
        job.status = JobStatus.FAILED
        job.updated_at = datetime.now(timezone.utc)
        job.error_message = error_message
        self.job_repository.update_job(job)

    def _build_knowledge_graph(self, doc_id: str, semantic_data) -> None:
        """
        Entity 노드, MENTIONS 관계 및 Entity-Entity 관계 생성
        """
        # [Spec 068] Program-Centric Star Schema Heuristic (Generalized)
        # Connect all extracted entities to the dynamically identified primary_entity node.
        program_node = semantic_data.primary_entity

        from app.core.utils import normalize_entity_name

        # 1. Entity 저장 및 MENTIONS 관계
        all_entity_names = set()
        for entity_type, names in semantic_data.entities.items():
            # semantic_data.entities is dict[EntityType, list[str]]
            for name in names:
                try:
                    # [Spec 069] Structural Normalization (Whitespace removal)
                    normalized_name = normalize_entity_name(name)

                    self.graph.save_entity(normalized_name, entity_type)
                    # We keep the mention relationship to the original or normalized?
                    # Let's use normalized for graph consistency
                    self.graph.create_mention_relationship(doc_id, normalized_name)
                    all_entity_names.add(normalized_name)

                    # Create implicit relationship to Primary Entity node if found
                    if program_node and normalized_name != normalize_entity_name(program_node):
                        norm_program = normalize_entity_name(program_node)
                        # [FIX] Use valid EntityType. "SHOW" is not valid.
                        self.graph.save_entity(norm_program, "CONCEPT")

                        self.graph.create_entity_relationship(
                            source_name=normalized_name, relationship_type="PART_OF_CONTEXT", target_name=norm_program
                        )
                except Exception as e:
                    logger.error(f"Failed to build graph for entity {name}: {e}")

        # [Spec 069] Layer 3: Semantic Alias Mapping
        if semantic_data.aliases:
            for canonical, aliases in semantic_data.aliases.items():
                try:
                    norm_canonical = normalize_entity_name(canonical)
                    self.graph.save_entity(norm_canonical, "CONCEPT")  # Fallback type

                    for alias in aliases:
                        norm_alias = normalize_entity_name(alias)
                        if norm_alias != norm_canonical:
                            self.graph.save_entity(norm_alias, "CONCEPT")
                            self.graph.create_entity_relationship(
                                source_name=norm_alias, relationship_type="ALIAS_OF", target_name=norm_canonical
                            )
                except Exception as e:
                    logger.warning(f"Failed to create ALIAS_OF relationships for {canonical}: {e}")

        # 2. Entity-Entity 관계 생성 (Spec 016)
        if hasattr(semantic_data, "relationships") and semantic_data.relationships:
            logger.info(f"Building graph with {len(semantic_data.relationships)} relationships for doc {doc_id}")
            for rel in semantic_data.relationships:
                try:
                    logger.debug(f"Processing relationship: {rel.source} -[{rel.relationship}]-> {rel.target}")

                    # 누락된 Entity 생성
                    if rel.source not in all_entity_names:
                        self.graph.save_entity(rel.source, rel.source_type)
                    if rel.target not in all_entity_names:
                        self.graph.save_entity(rel.target, rel.target_type)

                    # Relationship 생성
                    self.graph.create_entity_relationship(
                        source_name=rel.source, relationship_type=rel.relationship, target_name=rel.target
                    )
                    logger.debug(f"Created relationship: {rel.source}->{rel.target}")
                except Exception as e:
                    logger.error(f"Failed to create relationship {rel.source}->{rel.target}: {e}")
        else:
            logger.warning(f"No relationships found in semantic data for doc {doc_id}")
