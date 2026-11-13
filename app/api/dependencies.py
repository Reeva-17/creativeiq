from functools import lru_cache
from app.ai.groq_provider import GroqProvider
from app.ai.search_provider import TavilySearchProvider
from app.core.config import get_settings
from app.services.brand_analysis import BrandAnalysisService
from app.services.competitor_research import CompetitorResearchService
from app.services.report_generator import ReportGenerator
from app.services.swot_analysis import SWOTService


@lru_cache
def get_report_generator() -> ReportGenerator:
    settings = get_settings()
    provider = GroqProvider(settings.groq_api_key, settings.groq_model, settings.groq_timeout_seconds, settings.groq_max_retries)
    return ReportGenerator(BrandAnalysisService(provider), CompetitorResearchService(TavilySearchProvider(settings.tavily_api_key)), SWOTService())
