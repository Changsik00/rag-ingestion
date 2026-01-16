import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from neo4j import GraphDatabase

# Add project root to path to allow imports from app
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.domain.entities.job import IngestionJob, JobStatus
from app.infrastructure.storage.neo4j_job_repo import Neo4jJobRepository

# Configuration matching docker-compose defaults
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def seed_data():
    print(f"Connecting to Neo4j at {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("Connected successfully.")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    repo = Neo4jJobRepository(driver)

    print("Seeding dummy jobs...")
    
    now = datetime.now(timezone.utc)

    # 1. Successful Job
    job1 = IngestionJob(
        source_url="https://example.com/success",
        status=JobStatus.COMPLETED,
        created_at=now - timedelta(hours=2),
        updated_at=now - timedelta(hours=2, minutes=5)
    )
    repo.create_job(job1)
    print(f"Created COMPLETED job: {job1.job_id}")

    # 2. Pending Job (Queue Stuck?)
    job2 = IngestionJob(
        source_url="https://example.com/pending",
        status=JobStatus.PENDING,
        created_at=now - timedelta(minutes=30),
        updated_at=now - timedelta(minutes=30)
    )
    repo.create_job(job2)
    print(f"Created PENDING job: {job2.job_id}")

    # 3. Running Job
    job3 = IngestionJob(
        source_url="https://example.com/running",
        status=JobStatus.RUNNING,
        created_at=now - timedelta(minutes=5),
        updated_at=now - timedelta(minutes=5)
    )
    repo.create_job(job3)
    print(f"Created RUNNING job: {job3.job_id}")

    # 4. Failed Job
    job_fail_id = str(uuid.uuid4())
    job4 = IngestionJob(
        job_id=job_fail_id,
        source_url="https://example.com/fail",
        status=JobStatus.FAILED,
        created_at=now - timedelta(hours=1),
        updated_at=now - timedelta(hours=1),
        error_message="403 Forbidden: Cloudflare blocked the request"
    )
    repo.create_job(job4)
    print(f"Created FAILED job: {job4.job_id}")

    # 5. Retried Job (Linked to the Failed Job)
    job5 = IngestionJob(
        source_url="https://example.com/fail",
        status=JobStatus.COMPLETED,
        created_at=now - timedelta(minutes=10),
        updated_at=now - timedelta(minutes=8),
        retry_of=job_fail_id
    )
    repo.create_job(job5)
    print(f"Created RETRIED job (linked to {job_fail_id}): {job5.job_id}")

    driver.close()
    print("Done!")

if __name__ == "__main__":
    seed_data()
