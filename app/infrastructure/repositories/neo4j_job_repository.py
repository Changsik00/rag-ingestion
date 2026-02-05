import base64
from datetime import datetime

from neo4j import Driver

from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.job_repository import JobRepository


class Neo4jJobRepository(JobRepository):
    def __init__(self, driver: Driver):
        self.driver = driver

    def create_job(self, job: IngestionJob) -> None:
        query = """
        MERGE (j:IngestionJob {job_id: $job_id})
        SET j.source_url = $source_url,
            j.status = $status,
            j.created_at = $created_at,
            j.updated_at = $updated_at,
            j.error_message = $error_message,
            j.retry_of = $retry_of,
            j.raw_content = $raw_content,
            j.filename = $filename,
            j.content_hash = $content_hash,
            j.custom_metadata = $custom_metadata
        """
        # Encode bytes to base64 string for Neo4j storage
        raw_content_b64 = None
        if job.raw_content:
            raw_content_b64 = base64.b64encode(job.raw_content).decode("utf-8")
        
        # Serialize custom_metadata to JSON string if needed, or rely on Neo4j driver if it supports dict (it does for properties map, but limited types)
        # To be safe, let's keep it simple. If simple dict, Neo4j handles it? 
        # Actually Neo4j properties cannot be nested maps. They must be primitives or lists of primitives.
        # So we should JSON serialize custom_metadata.
        import json
        custom_metadata_json = json.dumps(job.custom_metadata) if job.custom_metadata else None

        params = {
            "job_id": job.job_id,
            "source_url": job.source_url,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "error_message": job.error_message,
            "retry_of": job.retry_of,
            "raw_content": raw_content_b64,
            "filename": job.filename,
            "content_hash": job.content_hash,
            "custom_metadata": custom_metadata_json,
        }
        with self.driver.session() as session:
            session.run(query, params)

    def update_job(self, job: IngestionJob) -> None:
        query = """
        MATCH (j:IngestionJob {job_id: $job_id})
        SET j.status = $status,
            j.updated_at = $updated_at,
            j.error_message = $error_message,
            j.docs_ids = $docs_ids,
            j.raw_content = $raw_content,
            j.filename = $filename,
            j.content_hash = $content_hash,
            j.custom_metadata = $custom_metadata
        """
        # Encode bytes to base64 string for Neo4j storage
        raw_content_b64 = None
        if job.raw_content:
            raw_content_b64 = base64.b64encode(job.raw_content).decode("utf-8")
        
        import json
        custom_metadata_json = json.dumps(job.custom_metadata) if job.custom_metadata else None

        params = {
            "job_id": job.job_id,
            "status": job.status.value,
            "updated_at": job.updated_at.isoformat(),
            "error_message": job.error_message,
            "docs_ids": job.docs_ids,
            "raw_content": raw_content_b64,
            "filename": job.filename,
            "content_hash": job.content_hash,
            "custom_metadata": custom_metadata_json,
        }
        with self.driver.session() as session:
            session.run(query, params)

    def get_job(self, job_id: str) -> IngestionJob | None:
        query = """
        MATCH (j:IngestionJob {job_id: $job_id})
        RETURN j
        """
        return self._fetch_single_job(query, job_id=job_id)

    def find_last_job_by_source(self, source_url: str) -> IngestionJob | None:
        query = """
        MATCH (j:IngestionJob {source_url: $source_url})
        WHERE j.status = 'COMPLETED'
        RETURN j
        ORDER BY j.created_at DESC
        LIMIT 1
        """
        return self._fetch_single_job(query, source_url=source_url)

    def list_jobs(self, limit: int = 50) -> list[IngestionJob]:
        query = """
        MATCH (j:IngestionJob)
        RETURN j
        ORDER BY j.created_at DESC
        LIMIT $limit
        """
        jobs = []
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            for record in result:
                jobs.append(self._map_node_to_job(record["j"]))
        return jobs

    def _fetch_single_job(self, query: str, **params) -> IngestionJob | None:
         with self.driver.session() as session:
            result = session.run(query, **params)
            record = result.single()
            if not record:
                return None
            return self._map_node_to_job(record["j"])

    def _map_node_to_job(self, node) -> IngestionJob:
        import json
        
        # Decode base64 back to bytes
        raw_content = None
        if node.get("raw_content"):
            raw_content = base64.b64decode(node["raw_content"])
            
        custom_metadata = None
        if node.get("custom_metadata"):
            try:
                custom_metadata = json.loads(node["custom_metadata"])
            except:
                custom_metadata = {}

        return IngestionJob(
            job_id=node["job_id"],
            source_url=node["source_url"],
            status=JobStatus(node["status"]),
            created_at=datetime.fromisoformat(node["created_at"]),
            updated_at=datetime.fromisoformat(node["updated_at"]),
            error_message=node.get("error_message"),
            retry_of=node.get("retry_of"),
            raw_content=raw_content,
            filename=node.get("filename"),
            docs_ids=node.get("docs_ids", []),
            content_hash=node.get("content_hash"),
            custom_metadata=custom_metadata,
        )
