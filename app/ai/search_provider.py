from abc import ABC, abstractmethod
from dataclasses import dataclass
import httpx
from app.core.exceptions import ProviderUnavailableError


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> list[SearchResult]: ...


class TavilySearchProvider(SearchProvider):
    """Optional public-web search adapter; replace this class for another provider."""
    def __init__(self, api_key: str | None): self.api_key = api_key

    async def search(self, query: str) -> list[SearchResult]:
        if not self.api_key: raise ProviderUnavailableError("TAVILY_API_KEY is not configured")
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post("https://api.tavily.com/search", json={"api_key": self.api_key, "query": query, "max_results": 5, "search_depth": "basic"})
        response.raise_for_status()
        return [SearchResult(title=row.get("title", "Untitled"), url=row["url"], snippet=row.get("content", "")) for row in response.json().get("results", []) if row.get("url")]
