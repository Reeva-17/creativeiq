from app.schemas.brand_input import BrandInput, CompetitorRequest
from app.schemas.brand_report import BrandIntelligenceReport, EvidenceType, Finding
from app.services.brand_analysis import BrandAnalysisService
from app.services.competitor_research import CompetitorResearchService
from app.services.swot_analysis import SWOTService


class ReportGenerator:
    def __init__(self, brand_service: BrandAnalysisService, competitor_service: CompetitorResearchService, swot_service: SWOTService):
        self.brand_service, self.competitor_service, self.swot_service = brand_service, competitor_service, swot_service

    async def complete(self, brand: BrandInput, competitors: list[str] | None = None) -> BrandIntelligenceReport:
        dna, visual, assumptions = await self.brand_service.analyze(brand)
        competitor_analysis = await self.competitor_service.research(CompetitorRequest(brand=brand, competitor_names=competitors or []))
        overview = [Finding(statement=f"{brand.brand_name} is a {brand.industry} brand.", evidence_type=EvidenceType.user_provided)]
        return BrandIntelligenceReport(brand_name=brand.brand_name, industry=brand.industry, executive_summary=overview, brand_overview=overview, brand_dna=dna, competitor_analysis=competitor_analysis, swot_analysis=self.swot_service.generate(dna, competitor_analysis), visual_identity=visual, key_takeaways=overview, assumptions=assumptions + competitor_analysis.limitations)
