from typing import List, Optional
from neo4j import Driver
from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.job_repository import JobRepository
from datetime import datetime

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
            j.retry_of = $retry_of
        """
        params = {
            "job_id": job.job_id,
            "source_url": job.source_url,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "error_message": job.error_message,
            "retry_of": job.retry_of
        }
        with self.driver.session() as session:
            session.run(query, params)

    def update_job(self, job: IngestionJob) -> None:
        query = """
        MATCH (j:IngestionJob {job_id: $job_id})
        SET j.status = $status,
            j.updated_at = $updated_at,
            j.error_message = $error_message
        """
        params = {
            "job_id": job.job_id,
            "status": job.status.value,
            "updated_at": job.updated_at.isoformat(),
            "error_message": job.error_message
        }
        with self.driver.session() as session:
            session.run(query, params)

    def get_job(self, job_id: str) -> Optional[IngestionJob]:
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
            return IngestionJob(
                job_id=node["job_id"],
                source_url=node["source_url"],
                status=JobStatus(node["status"]),
                created_at=datetime.fromisoformat(node["created_at"]),
                updated_at=datetime.fromisoformat(node["updated_at"]),
                error_message=node.get("error_message"),
                retry_of=node.get("retry_of")
            )

    def list_jobs(self, limit: int = 50) -> List[IngestionJob]:
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
                jobs.append(IngestionJob(
                    job_id=node["job_id"],
                    source_url=node["source_url"],
                    status=JobStatus(node["status"]),
                    created_at=datetime.fromisoformat(node["created_at"]),
                    updated_at=datetime.fromisoformat(node["updated_at"]),
                    error_message=node.get("error_message"),
                    retry_of=node.get("retry_of")
                ))
        return jobs
