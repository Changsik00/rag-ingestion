import os
import socket
import time

import pytest
from fastapi.testclient import TestClient

from app.interfaces.api.main import app

# Standard Seed Data
SEED_URLS = {
    "wikipedia": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "github": "https://github.com/langchain-ai/langchain",
}


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open on a host"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (TimeoutError, ConnectionRefusedError, OSError):
        return False


@pytest.fixture(scope="session", autouse=True)
def check_infrastructure():
    """
    Verify that required infrastructure (Neo4j, ChromaDB) is running before starting tests.
    If services are not reachable, skip all integration tests.
    """
    neo4j_host = os.getenv("NEO4J_HOST", "localhost")
    neo4j_port = int(os.getenv("NEO4J_PORT", 7687))
    chroma_host = os.getenv("CHROMA_HOST", "localhost")
    chroma_port = int(os.getenv("CHROMA_PORT", 8000))

    services = {
        "Neo4j": (neo4j_host, neo4j_port),
        "ChromaDB": (chroma_host, chroma_port),
    }

    missing_services = []

    for name, (host, port) in services.items():
        if not is_port_open(host, port):
            missing_services.append(f"{name} ({host}:{port})")

    if missing_services:
        pytest.skip(f"Infrastructure not ready: {', '.join(missing_services)}. Please run 'docker compose up -d'.")

    return True


@pytest.fixture(scope="session")
def api_client():
    """Session-scoped API Client with Lifespan Management"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def seed_test_data(check_infrastructure, api_client):
    """
    Ensure standard test data exists in the database.
    If not, trigger ingestion and wait for completion.
    Returns a dictionary of {name: document_content} or relevant metadata.
    """
    # 1. Check if data already exists (implied by idempotency or checking specific documents)
    # For now, we'll try to ingest. If duplicate logic exists, it handles it.

    seeded_jobs = {}

    # 2. Trigger Ingestion
    for name, url in SEED_URLS.items():
        response = api_client.post("/v1/ingest/web", json={"url": url})
        if response.status_code == 202:
            job_id = response.json()["job_id"]
            seeded_jobs[name] = job_id
        elif response.status_code == 200:
            # Synchronous or already exists
            pass

    # 3. Wait for Completion (Simple Polling)
    max_retries = 30
    for name, job_id in seeded_jobs.items():
        for _ in range(max_retries):
            # Assumes endpoint to check job status exists
            job_res = api_client.get(f"/v1/jobs/{job_id}")
            if job_res.status_code == 200:
                data = job_res.json()
                status = data.get("current_status") or data.get("status")
                if status == "COMPLETED":
                    break
                elif status == "FAILED":
                    pytest.fail(f"Seed data ingestion failed for {name} ({job_id})")
            time.sleep(1)

    return seeded_jobs
