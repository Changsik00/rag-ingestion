from duckduckgo_search import DDGS
from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str

class DuckDuckGoSearchClient:
    def __init__(self):
        self.ddgs = DDGS()

    async def search(self, query: str, num_results: int = 5, time_limit: str = None) -> list[SearchResult]:
        """
        Search DuckDuckGo for a given query.
        time_limit: 'd' (day), 'w' (week), 'm' (month), 'y' (year)
        """
        try:
            # DDGS().text() is synchronous, but fast enough for this use case.
            # If blocking becomes an issue, we can wrap it in run_in_executor.
            results = self.ddgs.text(query, max_results=num_results, timelimit=time_limit)
            
            search_results = []
            if results:
                for res in results:
                    search_results.append(SearchResult(
                        title=res.get("title", ""),
                        link=res.get("href", ""),
                        snippet=res.get("body", "")
                    ))
            return search_results
        except Exception as e:
            print(f"DuckDuckGo Search Error: {e}")
            return []
