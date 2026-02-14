import pytest
import respx
from httpx import Response

from app.infrastructure.external_api.google_search_client import GoogleSearchClient


@pytest.fixture
def client():
    return GoogleSearchClient(api_key="test_key", cse_id="test_cse")


@pytest.mark.asyncio
async def test_search_success(client):
    query = "test query"
    mock_response = {"items": [{"title": "Test Title", "link": "http://example.com", "snippet": "Test Snippet"}]}

    with respx.mock(base_url="https://www.googleapis.com") as respx_mock:
        respx_mock.get("/customsearch/v1").mock(return_value=Response(200, json=mock_response))

        results = await client.search(query)

        assert len(results) == 1
        assert results[0].title == "Test Title"
        assert results[0].link == "http://example.com"
        assert results[0].snippet == "Test Snippet"


@pytest.mark.asyncio
async def test_search_empty(client):
    query = "empty query"
    mock_response = {}  # No items

    with respx.mock(base_url="https://www.googleapis.com") as respx_mock:
        respx_mock.get("/customsearch/v1").mock(return_value=Response(200, json=mock_response))

        results = await client.search(query)

        assert len(results) == 0


@pytest.mark.asyncio
async def test_search_error(client):
    query = "error query"

    with respx.mock(base_url="https://www.googleapis.com") as respx_mock:
        respx_mock.get("/customsearch/v1").mock(return_value=Response(403, json={"error": "forbidden"}))

        with pytest.raises(Exception):  # httpx.HTTPStatusError
            await client.search(query)
