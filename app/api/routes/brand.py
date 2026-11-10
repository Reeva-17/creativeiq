from fastapi import APIRouter, Depends
from app.api.dependencies import get_report_generator
from app.schemas.brand_input import BrandInput
from app.schemas.brand_report import BrandDNA, BrandIntelligenceReport, VisualIdentity
from app.services.report_generator import ReportGenerator

router = APIRouter(prefix="/api/v1/brand", tags=["Brand intelligence"])


@router.post("/analyze", response_model=BrandIntelligenceReport, summary="Create the complete integration-ready brand intelligence report")
async def analyze_brand(brand: BrandInput, generator: ReportGenerator = Depends(get_report_generator)) -> BrandIntelligenceReport:
    return await generator.complete(brand)


@router.post("/analyze-dna", response_model=dict, summary="Analyze brand DNA without competitor research")
async def analyze_dna(brand: BrandInput, generator: ReportGenerator = Depends(get_report_generator)) -> dict:
    dna, visual, assumptions = await generator.brand_service.analyze(brand)
    return {"brand_name": brand.brand_name, "brand_dna": dna, "visual_identity": visual, "assumptions": assumptions}
