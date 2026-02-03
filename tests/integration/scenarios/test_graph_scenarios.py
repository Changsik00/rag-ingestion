import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.application.services.semantic_extractor import SemanticExtractor
from app.domain.value_objects.extracted_metadata import ExtractedMetadata
from app.domain.value_objects.ontology import EntityType
from app.interfaces.api.dependencies import get_scraper
from app.interfaces.api.main import app
from app.interfaces.api.v1.dto.ingest import IngestResponse

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_database():
    """Reset the database before each test for isolation."""
    # Use the integrity reset endpoint
    client.post("/v1/integrity/reset")
    # Wait a bit for the async reset to complete
    time.sleep(1)
    yield

@pytest.fixture
def mock_scraper_graph():
    mock = Mock()
    mock.scrape = AsyncMock(return_value=IngestResponse(
        url="https://example.com/elon-musk",
        markdown="""
        Elon Musk founded Tesla in 2003. He also founded SpaceX.
        Tesla headquarters is in Austin, Texas. Python is used for software.
        """,
        metadata={"title": "Elon Musk Bio", "source_id": "https://example.com/elon-musk"},
        message="Success"
    ))
    return mock

@pytest.mark.integration
class TestGraphScenarios:
    """
    Knowledge Graph & Entity Scenarios
    Pattern: Given-When-Then (GWT)
    """

    def test_entity_extraction_and_retrieval_flow(self, mock_scraper_graph):
        # Given: Ingestion request for entity-rich content with a unique URL
        import uuid
        url = f"https://example.com/elon-musk-{uuid.uuid4()}"
        unique_name = f"Musk-{uuid.uuid4().hex[:6]}"
        mock_scraper_graph.scrape.return_value.url = url

        app.dependency_overrides[get_scraper] = lambda: mock_scraper_graph
        try:
            with patch.object(SemanticExtractor, "extract", new_callable=AsyncMock) as mock_extract:
                mock_extract.return_value = ExtractedMetadata(
                    title="Elon Musk Bio",
                    summary="Elon Musk is the CEO of Tesla.",
                    keywords=["musk", "tesla"],
                    entities={EntityType.PERSON: [unique_name], EntityType.ORGANIZATION: ["Tesla"]},
                    language="en"
                )

                # When: Ingesting the document
                response = client.post("/v1/ingest/web", json={"url": url, "enable_extraction": True})
                job_id = response.json()["job_id"]

                # Wait for completion
                job_completed = False
                for _ in range(30):
                    job_resp = client.get(f"/v1/jobs/{job_id}")
                    if job_resp.json().get("current_status") == "COMPLETED":
                        job_completed = True
                        break
                    time.sleep(0.5)

                assert job_completed, f"Job {job_id} failed: {client.get(f'/v1/jobs/{job_id}').json()}"

                # Then: Entities are extracted and accessible via API
                ent_res = client.get("/v1/entities")
                assert ent_res.status_code == 200
                entities = ent_res.json()

                # Then: Specific unique entity exists in the list
                names = [e["name"].lower() for e in entities]
                assert any(unique_name.lower() in n for n in names), f"Expected {unique_name} in {names}"

                # Then: Relationships can be listed for a specific entity
                rel_res = client.get(f"/v1/entities/{unique_name}/relationships")
                if rel_res.status_code == 200:
                    assert isinstance(rel_res.json(), list)
        finally:
            app.dependency_overrides.clear()

    def test_hybrid_knowledge_consistency(self, mock_scraper_graph):
        """
        Scenario: Check that both Vector (Chroma) and Graph (Neo4j) store related info.
        """
        # Given: Documents with overlapping info and unique URL
        import uuid
        url = f"https://example.com/elon-consistency-{uuid.uuid4()}"
        unique_name = f"Tesla-Consist-{uuid.uuid4().hex[:6]}"
        mock_scraper_graph.scrape.return_value.url = url

        app.dependency_overrides[get_scraper] = lambda: mock_scraper_graph
        try:
            with patch.object(SemanticExtractor, "extract", new_callable=AsyncMock) as mock_extract:
                mock_extract.return_value = ExtractedMetadata(
                    title="Tesla Consistency Test",
                    summary="Tesla consistency check.",
                    keywords=["tesla"],
                    entities={EntityType.ORGANIZATION: [unique_name]},
                    language="en"
                )

                response = client.post("/v1/ingest/web", json={"url": url, "enable_extraction": True})
                job_id = response.json().get("job_id")

                # Wait for completion (Vector is fast but async job ensures everything)
                for _ in range(20):
                    job_resp = client.get(f"/v1/jobs/{job_id}")
                    if job_resp.json().get("current_status") == "COMPLETED":
                        break
                    time.sleep(0.5)

                # When: Searching for info about Tesla
                # Then: Found in documents (Vector)
                doc_res = client.get("/v1/documents")
                docs = doc_res.json()
                found = any(url in (d.get("metadata", {}).get("source_url", "")) or url in (d.get("id") or "") for d in docs)
                assert found, f"Could not find document with {url} in {docs}"

                # Then: Found in entities (Graph)
                ent_res = client.get("/v1/entities")
                assert any(unique_name.lower() in e["name"].lower() for e in ent_res.json()), f"Expected {unique_name} in {ent_res.json()}"
        finally:
            app.dependency_overrides.clear()

    def test_entity_deduplication_and_mentions(self):
        """
        Scenario: Entity deduplication and mention count tracking (BDD/test_knowledge_graph.py)
        """
        from app.application.services.semantic_extractor import SemanticExtractor
        from app.domain.value_objects.extracted_metadata import ExtractedMetadata
        from app.domain.value_objects.ontology import EntityType
        from app.interfaces.api.dependencies import get_scraper

        unique_name = f"Dedupe-Entity-{int(time.time())}"
        url = f"https://example.com/dedupe-{int(time.time())}"

        mock_scraper = Mock()
        mock_scraper.scrape = AsyncMock(return_value=IngestResponse(
            url=url, markdown="Dedupe test content",
            metadata={"title": "Dedupe Test", "source_id": url},
            message="Success"
        ))

        app.dependency_overrides[get_scraper] = lambda: mock_scraper

        try:
            # When: Ingesting the same entity from two different sources (URLs)
            for i in range(2):
                current_url = f"{url}-{i}"
                mock_scraper.scrape.return_value.url = current_url
                mock_scraper.scrape.return_value.metadata["source_id"] = current_url
                
                with patch.object(SemanticExtractor, "extract", new_callable=AsyncMock) as mock_extract:
                    mock_extract.return_value = ExtractedMetadata(
                        title=f"Dedupe Doc {i}",
                        summary="Dedupe check",
                        keywords=["dedupe"],
                        entities={EntityType.PERSON: [unique_name]},
                        language="en"
                    )
                    
                    response = client.post("/v1/ingest/web", json={"url": current_url, "enable_extraction": True})
                    job_id = response.json().get("job_id")
                    
                    # Wait for completion
                    for _ in range(20):
                        job_resp = client.get(f"/v1/jobs/{job_id}")
                        if job_resp.json().get("current_status") == "COMPLETED":
                            break
                        time.sleep(0.5)

            # Then: Entity list should contain only one instance of the entity (Deduplicated)
            ent_res = client.get("/v1/entities")
            matches = [e for e in ent_res.json() if e["name"] == unique_name]
            assert len(matches) == 1, f"Expected 1 entity but found {len(matches)}"

            # Then: GET /entities/{name}/documents should return 2 unique documents (Mention tracking)
            doc_res = client.get(f"/v1/entities/{unique_name}/documents")
            assert doc_res.status_code == 200
            docs = doc_res.json()
            assert len(docs) >= 2
            
            # Then: Entity info should be accessible
            info_res = client.get(f"/v1/entities/{unique_name}/info")
            assert info_res.status_code == 200
            assert info_res.json()["name"] == unique_name

        finally:
            app.dependency_overrides.clear()

