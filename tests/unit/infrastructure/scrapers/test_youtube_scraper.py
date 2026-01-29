from unittest.mock import MagicMock, patch

import pytest

from app.infrastructure.scrapers.youtube_scraper import YouTubeScraper
from app.schemas.ingest import IngestResponse


@pytest.fixture
def scraper():
    return YouTubeScraper()


@pytest.mark.asyncio
async def test_youtube_scraper_with_transcript(scraper):
    """
    Test YouTubeScraper when transcript is available.
    """
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    mock_transcript = [
        {"text": "Hello world", "start": 0.0, "duration": 2.0},
        {"text": "This is a test", "start": 2.5, "duration": 3.0},
    ]

    # Mock youtube-transcript-api
    mock_transcript_obj = MagicMock()
    mock_transcript_obj.fetch.return_value = mock_transcript

    # Mock the return value of YouTubeTranscriptApi().list(video_id)
    with patch("app.infrastructure.scrapers.youtube_scraper.YouTubeTranscriptApi") as mock_api:
        mock_instance = mock_api.return_value
        mock_instance.list.return_value.find_transcript.return_value = mock_transcript_obj
        # Mock LLM extraction (since it's part of the scraper's scrape method)
        with patch(
            "app.infrastructure.scrapers.youtube_scraper.YouTubeScraper._extract_knowledge_with_llm"
        ) as mock_llm:
            mock_llm.return_value = {
                "summary": "Moked summary",
                "sections": [{"topic": "Introduction", "start": 0, "end": 5}],
                "claims": [{"text": "Test claim", "timestamp": "0:01"}],
                "tone": "Neutral",
                "intent": "Testing",
            }

            response = await scraper.scrape(url)

            assert isinstance(response, IngestResponse)
            assert str(response.url) == url
            assert "Moked summary" in response.markdown
            assert response.metadata["title"] != "Untitled Document"
            assert response.metadata["knowledge"]["intent"] == "Testing"


@pytest.mark.asyncio
async def test_youtube_scraper_fallback_to_whisper(scraper):
    """
    Test YouTubeScraper fallback to Whisper when no transcript is found.
    """
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # Mock Exception for Transcript API to trigger fallback
    with patch("app.infrastructure.scrapers.youtube_scraper.YouTubeTranscriptApi") as mock_api:
        mock_api.return_value.list.side_effect = Exception("No transcript")
        with patch(
            "app.infrastructure.scrapers.youtube_scraper.YouTubeScraper._extract_audio", return_value="/tmp/test.mp3"
        ):
            with patch(
                "app.infrastructure.scrapers.youtube_scraper.YouTubeScraper._run_whisper",
                return_value=[{"text": "Whisper text", "start": 0.0, "end": 5.0}],
            ):
                with patch(
                    "app.infrastructure.scrapers.youtube_scraper.YouTubeScraper._extract_knowledge_with_llm"
                ) as mock_llm:
                    mock_llm.return_value = {
                        "summary": "Whisper summary",
                        "sections": [],
                        "claims": [],
                        "tone": "",
                        "intent": "",
                    }

                    response = await scraper.scrape(url)

                    assert str(response.url) == url
                    assert "Whisper summary" in response.markdown
