from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.news import NewsCategory


class NewsClassifierProvider(ABC):
    """Abstract base class for news classification providers."""

    @abstractmethod
    async def classify(self, title: str, summary: str, company_name: str) -> Dict[str, Any]:
        """
        Classify a news article.

        Returns:
            Dict with:
            - category: NewsCategory
            - relevance_score: 1-10
            - urgency_score: 1-10
            - commercial_score: 1-10
            - risk_score: 1-10
            - confidence_score: 1-10
        """
        pass


class MockNewsClassifier(NewsClassifierProvider):
    """Mock classifier for development/testing."""

    async def classify(self, title: str, summary: str, company_name: str) -> Dict[str, Any]:
        """Return mock classification."""
        # Simple heuristics for mock
        keywords_map = {
            "partnership": NewsCategory.PARTNERSHIP,
            "acquisition": NewsCategory.ACQUISITION,
            "merger": NewsCategory.MERGER,
            "investment": NewsCategory.INVESTMENT,
            "cyber": NewsCategory.CYBER_INCIDENT,
            "breach": NewsCategory.DATA_BREACH,
            "new office": NewsCategory.NEW_OFFICE,
            "digital": NewsCategory.DIGITAL_PROJECT,
        }

        text = (title + " " + summary).lower()
        category = NewsCategory.OTHER

        for keyword, cat in keywords_map.items():
            if keyword in text:
                category = cat
                break

        return {
            "category": category.value,
            "relevance_score": 7,
            "urgency_score": 5,
            "commercial_score": 6,
            "risk_score": 4,
            "confidence_score": 8,
        }


class NewsClassifier:
    """Facade for news classification with pluggable providers."""

    def __init__(self, provider: NewsClassifierProvider = None):
        self.provider = provider or MockNewsClassifier()

    async def classify(self, title: str, summary: str, company_name: str) -> Dict[str, Any]:
        """Classify a news article."""
        return await self.provider.classify(title, summary, company_name)
