from app.schemas.brand_input import CompetitorRequest
from app.schemas.brand_report import CompetitorAnalysis, CompetitorProfile, EvidenceType, Finding
from app.ai.search_provider import SearchProvider
from app.core.exceptions import ProviderUnavailableError


class CompetitorResearchService:
    def __init__(self, search_provider: SearchProvider | None = None): self.search_provider = search_provider

    async def research(self, request: CompetitorRequest) -> CompetitorAnalysis:
        # Names are preserved but no claims are fabricated without a configured search provider.
        profiles = [CompetitorProfile(name=name, category="direct", research_status="name supplied; no public-source research was configured") for name in request.competitor_names]
        limitations = ["No search provider is configured in this standalone module; competitor claims are intentionally unavailable."]
        if self.search_provider and not profiles:
            try:
                results = await self.search_provider.search(f"leading {request.brand.industry} competitors")
                profiles = [CompetitorProfile(name=result.title, category="direct", research_status="search result; requires human validation", source_urls=[result.url], positioning=Finding(statement=result.snippet or "Search result did not include a description.", evidence_type=EvidenceType.verified, source_urls=[result.url])) for result in results]
                limitations = ["Search snippets are public-source leads, not a substitute for full website verification. Direct/indirect categorisation requires human validation."]
            except (ProviderUnavailableError, Exception) as exc:
                limitations = [f"Public competitor search unavailable: {exc}"]
        if request.research_urls:
            limitations.append("Research URLs were received but URL extraction is not enabled; they are retained as sources only.")
            for p in profiles: p.source_urls = [str(url) for url in request.research_urls]
        gaps = [Finding(statement="Competitor gap analysis requires sourced competitor observations.", evidence_type=EvidenceType.unavailable)]
        return CompetitorAnalysis(direct_competitors=profiles, market_gaps=gaps, limitations=limitations)
