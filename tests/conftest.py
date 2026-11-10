import pytest
from fastapi.testclient import TestClient
from app.api.dependencies import get_report_generator
from app.ai.provider import LLMProvider
from app.main import app
from app.services.brand_analysis import BrandAnalysisService
from app.services.competitor_research import CompetitorResearchService
from app.services.report_generator import ReportGenerator
from app.services.swot_analysis import SWOTService


class FakeProvider(LLMProvider):
    async def generate_json(self, prompt: str):
        return {"brand_dna": {"personality": [{"statement": "Approachable", "evidence_type": "ai_generated_interpretation"}]}, "visual_identity": {"visual_direction": {"statement": "Clean layouts", "evidence_type": "recommendation"}}}


@pytest.fixture
def client():
    generator = ReportGenerator(BrandAnalysisService(FakeProvider()), CompetitorResearchService(), SWOTService())
    app.dependency_overrides[get_report_generator] = lambda: generator
    yield TestClient(app)
    app.dependency_overrides.clear()
