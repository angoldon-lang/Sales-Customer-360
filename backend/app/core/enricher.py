from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class CompanyEnricherProvider(ABC):
    """Abstract base class for company enrichment providers."""

    @abstractmethod
    async def enrich(self, company_name: str, vat_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Enrich company data with website, sector, country, etc.

        Returns:
            Dict with keys: website, sector, country, status (active/needs_review)
        """
        pass


class MockCompanyEnricher(CompanyEnricherProvider):
    """Mock enricher for development/testing."""

    async def enrich(self, company_name: str, vat_number: Optional[str] = None) -> Dict[str, Any]:
        """Return mock enriched data."""
        # In a real implementation, would call web search APIs
        # For now, return sensible defaults
        return {
            "website": f"https://www.{company_name.lower().replace(' ', '-')}.com",
            "sector": "Technology",
            "country": "IT",
            "status": "needs_review" if not vat_number else "active",
        }


class CompanyEnricher:
    """Facade for company enrichment with pluggable providers."""

    def __init__(self, provider: Optional[CompanyEnricherProvider] = None):
        self.provider = provider or MockCompanyEnricher()

    async def enrich(self, company_name: str, vat_number: Optional[str] = None) -> Dict[str, Any]:
        """Enrich company data."""
        return await self.provider.enrich(company_name, vat_number)
