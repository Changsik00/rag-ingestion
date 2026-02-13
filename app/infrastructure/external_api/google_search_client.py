import os
from typing import List, Dict, Optional
import httpx
from pydantic import BaseModel

from app.core.config import get_settings

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str

class GoogleSearchClient:
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Search Google using Custom Search JSON API.
        
        Args:
            query: The search term.
            num_results: Number of results to return (max 10 per request).
            
        Returns:
            List of SearchResult objects.
        """
        if not self.api_key or not self.cse_id:
            raise ValueError("Google API Key and CSE ID must be configured.")

        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(num_results, 10),  # API limit is 10
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        if "items" in data:
            for item in data["items"]:
                results.append(SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", "")
                ))
        
        return results
