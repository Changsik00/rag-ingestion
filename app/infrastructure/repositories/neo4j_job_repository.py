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
            j.filename = $filename
        """
        # Encode bytes to base64 string for Neo4j storage
        raw_content_b64 = None
        if job.raw_content:
            raw_content_b64 = base64.b64encode(job.raw_content).decode("utf-8")

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
            j.filename = $filename
        """
        # Encode bytes to base64 string for Neo4j storage
        raw_content_b64 = None
        if job.raw_content:
            raw_content_b64 = base64.b64encode(job.raw_content).decode("utf-8")

        params = {
            "job_id": job.job_id,
            "status": job.status.value,
            "updated_at": job.updated_at.isoformat(),
            "error_message": job.error_message,
            "docs_ids": job.docs_ids,
            "raw_content": raw_content_b64,
            "filename": job.filename,
        }
        with self.driver.session() as session:
            session.run(query, params)

    def get_job(self, job_id: str) -> IngestionJob | None:
        query = """
        MATCH (j:IngestionJob {job_id: $job_id})
        RETURN j
        """
        with self.driver.session() as session:
            result = session.run(query, job_id=job_id)
            record = result.single()
            if not record:
                return None

            node = record["j"]

            # Decode base64 back to bytes
            raw_content = None
            if node.get("raw_content"):
                raw_content = base64.b64decode(node["raw_content"])

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
            )

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
                node = record["j"]

                # Decode base64 back to bytes
                raw_content = None
                if node.get("raw_content"):
                    raw_content = base64.b64decode(node["raw_content"])

                jobs.append(
                    IngestionJob(
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
                    )
                )
        return jobs
