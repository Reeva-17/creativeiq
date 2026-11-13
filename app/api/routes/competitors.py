from fastapi import APIRouter, Depends
from app.api.dependencies import get_report_generator
from app.schemas.brand_input import CompetitorRequest
from app.schemas.brand_report import CompetitorAnalysis
from app.services.report_generator import ReportGenerator

router = APIRouter(prefix="/api/v1/brand", tags=["Competitor research"])


@router.post("/competitors", response_model=CompetitorAnalysis, summary="Research provided competitors with transparent source limitations")
async def research_competitors(request: CompetitorRequest, generator: ReportGenerator = Depends(get_report_generator)) -> CompetitorAnalysis:
    return await generator.competitor_service.research(request)
