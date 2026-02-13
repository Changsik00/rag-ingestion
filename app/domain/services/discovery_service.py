import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

from app.application.services.ingestion import Ingestion
from app.infrastructure.external_api.google_search_client import GoogleSearchClient

logger = logging.getLogger(__name__)


class DiscoveryService:
    def __init__(
        self,
        search_client: GoogleSearchClient,
        ingestion_service: Ingestion,
    ):
        self.search_client = search_client
        self.ingestion_service = ingestion_service
        self.blocked_domains = {
            "youtube.com",
            "youtu.be",
            "facebook.com",
            "twitter.com",
            "instagram.com",
            "linkedin.com",
            "tiktok.com",
            "pinterest.com",
            "reddit.com",
        }
        self.blocked_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".mp4", ".mp3", ".zip", ".exe"}

    async def search_topic(self, topic: str, max_results: int = 5) -> list[dict]:
        """
        Search for a topic and return results without ingesting.
        Returns: List of dicts with title, link, snippet.
        """
        logger.info(f"Searching topic: '{topic}' (Max: {max_results})")
        try:
            results = await self.search_client.search(topic, num_results=max_results)
            return [
                {"title": r.title, "link": r.link, "snippet": r.snippet}
                for r in results
                if not self._is_blocked(r.link)
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def start_discovery(self, topic: str, max_depth: int = 1, max_docs: int = 10) -> list[str]:
        """
        Start autonomous discovery for a topic.
        1. Search Google for seed URLs.
        2. Crawl (BFS) to find more links up to max_depth.
        3. Trigger Ingestion for each valid URL.
        """
        logger.info(f"Starting discovery for topic: '{topic}' (Depth: {max_depth}, Max Docs: {max_docs})")

        # 1. Google Search
        try:
            search_results = await self.search_client.search(topic, num_results=max_docs)
            seed_urls = [res.link for res in search_results]
            logger.info(f"Found {len(seed_urls)} seed URLs from Google")
        except Exception as e:
            logger.error(f"Google Search failed: {e}")
            return []

        # 2. BFS Crawling
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(url, 0) for url in seed_urls]
        ingested_job_ids: list[str] = []
        ingested_count = 0

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            while queue and ingested_count < max_docs:
                url, current_depth = queue.pop(0)

                if url in visited:
                    continue
                visited.add(url)

                if self._is_blocked(url):
                    logger.debug(f"Skipping blocked URL: {url}")
                    continue

                # Trigger Ingestion
                try:
                    logger.info(f"Ingesting URL: {url} (Depth: {current_depth})")
                    job = await self.ingestion_service.ingest_url(url=url)
                    ingested_job_ids.append(job.job_id)
                    ingested_count += 1
                except Exception as e:
                    logger.error(f"Failed to ingest URL {url}: {e}")
                    # Continue to crawl even if ingestion fails?
                    # Usually we want to crawl only if we can access it.

                # Recursive Step
                if current_depth < max_depth:
                    try:
                        links = await self._fetch_links(client, url)
                        logger.debug(f"Found {len(links)} links on {url}")
                        for link in links:
                            if link not in visited:
                                queue.append((link, current_depth + 1))
                    except Exception as e:
                        logger.warning(f"Failed to fetch links from {url}: {e}")

        logger.info(f"Discovery complete. Ingested {ingested_count} documents.")
        return ingested_job_ids

    def _is_blocked(self, url: str) -> bool:
        """Check against blocklist (domains and extensions)."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # Domain Check (includes subdomains)
        if any(blocked in domain for blocked in self.blocked_domains):
            return True

        # Extension Check
        if any(path.endswith(ext) for ext in self.blocked_extensions):
            return True

        return False

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def _fetch_links(self, client: httpx.AsyncClient, url: str) -> list[str]:
        """Fetch HTML and extract valid links."""
        try:
            response = await client.get(url)
            response.raise_for_status()

            # Simple content type check
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full_url = urljoin(url, href)
                # Basic validation
                parsed = urlparse(full_url)
                if parsed.scheme in ("http", "https"):
                    links.append(full_url)

            return links
        except Exception:
            raise
