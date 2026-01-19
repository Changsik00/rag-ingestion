from datetime import datetime, timezone
from uuid import UUID

from app.core.exceptions import DoitException
from app.core.logging_config import setup_logger
from app.domain.entities.document import AtomicDocument
from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.interfaces.job_repository import JobRepository
from app.domain.interfaces.scraper import ScraperInterface
from app.domain.services.semantic_extractor import SemanticExtractor

logger = setup_logger(__name__)

class IngestionService:
    def __init__(
        self,
        scraper: ScraperInterface,
        repository: DocumentRepository,
        graph: GraphRepository,
        job_repository: JobRepository,
        extractor: SemanticExtractor | None = None,
    ):
        self.scraper = scraper
        self.repository = repository
        self.graph = graph
        self.job_repository = job_repository
        self.extractor = extractor

    def create_job(self, url: str, retry_of: str | None = None) -> IngestionJob:
        """Create and persist a new job in PENDING state."""
        job = IngestionJob(source_url=url, status=JobStatus.PENDING, retry_of=retry_of)
        self.job_repository.create_job(job)
        return job

    def process_job(self, job_id: str) -> None:
        """Execute the ingestion logic asynchronously."""
        job = self.job_repository.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found during processing start")
            return

        try:
            # 1. Update Status to RUNNING
            logger.info(f"Starting ingestion job {job_id} for {job.source_url}")
            job.status = JobStatus.RUNNING
            job.updated_at = datetime.now(timezone.utc)
            self.job_repository.update_job(job)

            # 2. Scrape
            result = self.scraper.scrape(job.source_url)

            # 3. Semantic Extraction (Spec 005)
            semantic_data = None
            if self.extractor:
                try:
                    semantic_data = self.extractor.extract(result.markdown)
                    if semantic_data:
                        # Append semantic data to metadata
                        result.metadata["semantic_data"] = semantic_data.model_dump()
                except Exception as e:
                    # Extraction failure should not fail the entire job, but log it
                    logger.warning(f"Semantic extraction failed for job {job_id}: {e}")

            # 4. Map to Domain Entity
            doc = AtomicDocument(content=result.markdown, source_url=str(result.url), metadata=result.metadata)

            # 5. Save Document
            self.repository.save(doc)

            # 6. Build Knowledge Graph (Spec 010 + 016)
            if semantic_data:
                self._build_knowledge_graph(doc.id, semantic_data)

            # 7. Update Job (COMPLETED)
            job.status = JobStatus.COMPLETED
            job.updated_at = datetime.now(timezone.utc)
            self.job_repository.update_job(job)
            logger.info(f"Ingestion job {job_id} completed successfully")

        except DoitException as e:
            # Known domain/infrastructure exceptions
            logger.error(f"Ingestion failed for job {job_id}: {str(e)}")
            self._fail_job(job, str(e))
        except Exception as e:
            # Unexpected system errors
            logger.exception(f"Unexpected error in ingestion job {job_id}")
            self._fail_job(job, f"System Error: {str(e)}")

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
        if not semantic_data.entities:
            return

        # 1. Entity 저장 및 MENTIONS 관계
        all_entity_names = set()
        for entity_type, names in semantic_data.entities.items():
            for name in names:
                try:
                    self.graph.save_entity(name, entity_type)
                    self.graph.create_mention_relationship(str(doc_id), name)
                    all_entity_names.add(name)
                except Exception as e:
                    logger.error(f"Failed to build graph for entity {name}: {e}")

        # 2. Entity-Entity 관계 생성 (Spec 016)
        if hasattr(semantic_data, "relationships") and semantic_data.relationships:
            for rel in semantic_data.relationships:
                try:
                    # 누락된 Entity 생성
                    if rel.source not in all_entity_names:
                        self.graph.save_entity(rel.source, rel.source_type)
                    if rel.target not in all_entity_names:
                        self.graph.save_entity(rel.target, rel.target_type)

                    # Relationship 생성
                    self.graph.create_entity_relationship(
                        source_name=rel.source, relationship_type=rel.relationship, target_name=rel.target
                    )
                except Exception as e:
                    logger.error(f"Failed to create relationship {rel.source}->{rel.target}: {e}")
