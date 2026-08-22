from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, timedelta


class NewsSearchProvider(ABC):
    """Abstract base class for news search providers."""

    @abstractmethod
    async def search(self, query: str, company_website: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for news articles.

        Returns:
            List of dicts with: title, url, source, published_date, summary
        """
        pass


class MockNewsSearcher(NewsSearchProvider):
    """Mock news searcher for development/testing."""

    async def search(self, query: str, company_website: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Return mock news articles."""
        base_date = datetime.utcnow()
        return [
            {
                "title": f"Breaking: {query} announces new partnership",
                "url": "https://example.com/news1",
                "source": "Financial Times",
                "published_date": (base_date - timedelta(days=1)).isoformat(),
                "summary": f"Company {query} has announced a strategic partnership with a major tech firm.",
            },
            {
                "title": f"{query} invests in digital transformation",
                "url": "https://example.com/news2",
                "source": "Forbes",
                "published_date": (base_date - timedelta(days=3)).isoformat(),
                "summary": f"{query} has allocated significant resources to digital transformation initiatives.",
            },
        ]


class NewsSearcher:
    """Facade for news search with pluggable providers."""

    def __init__(self, provider: NewsSearchProvider = None):
        self.provider = provider or MockNewsSearcher()

    async def search(self, query: str, company_website: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Search for news articles."""
        return await self.provider.search(query, company_website, limit)
