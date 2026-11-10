import pytest
from app.ai.provider import LLMProvider
from app.core.exceptions import ProviderResponseError
from app.schemas.brand_input import BrandInput
from app.services.brand_analysis import BrandAnalysisService
from app.services.report_generator import ReportGenerator
from app.services.competitor_research import CompetitorResearchService
from app.services.swot_analysis import SWOTService


class BrokenProvider(LLMProvider):
    async def generate_json(self, prompt): raise ProviderResponseError("malformed JSON")


@pytest.mark.asyncio
async def test_failed_llm_is_reported_not_faked():
    dna, visual, assumptions = await BrandAnalysisService(BrokenProvider()).analyze(BrandInput(brand_name="Glowify", industry="Skincare"))
    assert dna.identity[0].evidence_type.value == "user_provided_information"
    assert any("AI enrichment unavailable" in x for x in assumptions)


@pytest.mark.asyncio
async def test_end_to_end_no_key_provider():
    from app.ai.groq_provider import GroqProvider
    report = await ReportGenerator(BrandAnalysisService(GroqProvider(None, "test")), CompetitorResearchService(), SWOTService()).complete(BrandInput(brand_name="Glowify", industry="Skincare"))
    assert report.brand_name == "Glowify"
    assert report.competitor_analysis.limitations
