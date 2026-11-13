import pytest
from app.schemas.brand_input import BrandInput, CompetitorRequest
from app.services.competitor_research import CompetitorResearchService


@pytest.mark.asyncio
async def test_supplied_competitor_is_not_researched_without_sources():
    result = await CompetitorResearchService().research(CompetitorRequest(brand=BrandInput(brand_name="Glowify", industry="Skincare"), competitor_names=["Sample Co"]))
    assert result.direct_competitors[0].research_status.startswith("name supplied")
    assert result.market_gaps[0].evidence_type.value == "unavailable"


@pytest.mark.asyncio
async def test_empty_competitors_returns_limitations():
    result = await CompetitorResearchService().research(CompetitorRequest(brand=BrandInput(brand_name="Glowify", industry="Skincare")))
    assert result.direct_competitors == []
    assert result.limitations
