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

    async def process_job(self, job_id: str) -> None:
        """Execute the ingestion logic asynchronously."""
        job = self.job_repository.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} NOT FOUND in repository!")
            return

        try:
            # [Spec 065] 1. Immediate ID/URL-based Deduplication Check
            custom_meta = job.custom_metadata or {}
            is_forced = custom_meta.get("force_refresh") is True

            if not is_forced:
                # Direct check for latest meaningful job for this URL
                last_job = self.job_repository.find_last_job_by_source(
                    job.source_url,
                    exclude_job_id=job_id,
                    statuses=[JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING],
                )

                if last_job and last_job.status in [JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING]:
                    logger.info(f"Job {job_id} skipping because of duplicate {last_job.job_id} ({last_job.status})")
                    job.status = JobStatus.SKIPPED
                    job.updated_at = datetime.now(timezone.utc)
                    self.job_repository.update_job(job)
                    return

                # 2. Strategy-based check (Contents, TTL, Metadata-specific)
                strategy = self.deduplication_factory.get_strategy(job.source_url)
                if await strategy.is_duplicate(job):
                    logger.info(f"Job {job_id} detected as duplicate via {type(strategy).__name__}. Skipping.")
                    job.status = JobStatus.SKIPPED
                    job.updated_at = datetime.now(timezone.utc)
                    self.job_repository.update_job(job)
                    return

            # 3. If not duplicate, Update Status to RUNNING and proceed
            logger.info(f"Starting ingestion job {job_id} for {job.source_url}")
            job.status = JobStatus.RUNNING
            job.updated_at = datetime.now(timezone.utc)
            self.job_repository.update_job(job)

            if job.raw_content and job.filename:
                logger.info(f"Processing local file: {job.filename}")
                from app.core.file_processor import FileProcessor

                file_processor = FileProcessor()
                segments = file_processor.extract_segments(job.raw_content, job.filename)
            else:
                result = await self.scraper.scrape(job.source_url)
                segments = [(result.markdown, result.metadata)]

            job.docs_ids = []

            # 3. Process each segment
            for text, metadata in segments:
                # Semantic Extraction (Spec 005)
                semantic_data = None
                if self.extractor:
                    try:
                        semantic_data = await self.extractor.extract(text, metadata=metadata, thread_id=job_id)
                        if semantic_data:
                            metadata["semantic_data"] = semantic_data.model_dump()
                    except Exception as e:
                        logger.warning(f"Semantic extraction failed for segment in job {job_id}: {e}")

                # Map to Domain Entity
                doc_metadata = metadata.copy()
                doc_metadata["source_url"] = str(job.source_url)
                if "source_id" not in doc_metadata:
                    doc_metadata["source_id"] = str(job.source_url)
                
                # [Spec 068 Fix] Ensure primary_entity is passed to the document node
                if semantic_data and semantic_data.primary_entity:
                    doc_metadata["primary_entity"] = semantic_data.primary_entity

                doc = Document(content=text, metadata=doc_metadata)

                # Chunking & Save
                chunker = self._get_chunker(job.chunking_config)
                chunks = chunker.chunk_document(doc)
                self.repository.save_with_chunks(doc, chunks)
                job.docs_ids.append(doc.id)

                # Build Knowledge Graph (Spec 010 + 016)
                if semantic_data:
                    self._build_knowledge_graph(UUID(doc.id), semantic_data)

            # 4. Update Job (COMPLETED)
            job.status = JobStatus.COMPLETED
            job.updated_at = datetime.now(timezone.utc)
            self.job_repository.update_job(job)
            logger.info(f"Ingestion job {job_id} completed with {len(job.docs_ids)} documents")

        except BaseAppError as e:
            # Known domain/infrastructure exceptions
            logger.error(f"Ingestion failed for job {job_id}: {str(e)}")
            self._fail_job(job, str(e))
        except Exception as e:
            # Unexpected system errors
            logger.exception(f"Unexpected error in ingestion job {job_id}")
            self._fail_job(job, f"System Error: {str(e)}")
        finally:
            # [Spec 060] Safety: Auto-cleanup history on Terminal States
            # We must NOT delete if the job is PENDING/RUNNING (e.g. HITL Pause)
            # Only clean up if it's truly done (Success or Failed) AND cleanup is enabled.
            from app.core.config import get_settings

            if get_settings().AUTO_CLEANUP_ENABLED:
                try:
                    # Reload job status to be sure
                    final_job = self.job_repository.get_job(job_id)
                    if final_job and final_job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                        if self.extractor:
                            logger.info(f"Auto-Cleaning history for job {job_id} (Status: {final_job.status})")
                            await self.extractor.cleanup(job_id)
                except Exception as cleanup_error:
                    logger.error(f"Failed to auto-clean history for job {job_id}: {cleanup_error}")
            else:
                logger.info(f"Auto-Cleanup skipped (AUTO_CLEANUP_ENABLED=False) for job {job_id}")

    def _fail_job(self, job: IngestionJob, error_message: str) -> None:
        """Helper to mark job as failed."""
        job.status = JobStatus.FAILED
        job.updated_at = datetime.now(timezone.utc)
        job.error_message = error_message
        self.job_repository.update_job(job)

    def _build_knowledge_graph(self, doc_id: UUID, semantic_data) -> None:
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
                    self.graph.create_mention_relationship(str(doc_id), normalized_name)
                    all_entity_names.add(normalized_name)
                    
                    # Create implicit relationship to Primary Entity node if found
                    if program_node and normalized_name != normalize_entity_name(program_node):
                        norm_program = normalize_entity_name(program_node)
                        self.graph.save_entity(norm_program, "SHOW") 
                        
                        self.graph.create_entity_relationship(
                            source_name=normalized_name,
                            relationship_type="PART_OF_CONTEXT", 
                            target_name=norm_program
                        )
                except Exception as e:
                    logger.error(f"Failed to build graph for entity {name}: {e}")

        # [Spec 069] Layer 3: Semantic Alias Mapping
        if semantic_data.aliases:
            for canonical, aliases in semantic_data.aliases.items():
                try:
                    norm_canonical = normalize_entity_name(canonical)
                    self.graph.save_entity(norm_canonical, "CONCEPT") # Fallback type
                    
                    for alias in aliases:
                        norm_alias = normalize_entity_name(alias)
                        if norm_alias != norm_canonical:
                            self.graph.save_entity(norm_alias, "CONCEPT")
                            self.graph.create_entity_relationship(
                                source_name=norm_alias,
                                relationship_type="ALIAS_OF",
                                target_name=norm_canonical
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
