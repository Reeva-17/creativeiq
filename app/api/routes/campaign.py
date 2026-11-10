import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.schemas.campaign_schema import (
    CampaignInput,
    CreativeDirectorHandoff
)
from app.services.langgraph_creative_director import autonomous_creative_director
from app.core.config import settings

router = APIRouter(prefix="/api/v1/campaign", tags=["Person 2 · Creative Director"])


class FromReportRequest(BaseModel):
    report: Dict[str, Any]
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    campaign_objective: Optional[str] = None
    budget: Optional[str] = None
    duration: Optional[str] = "30 Days"


@router.post(
    "/generate",
    response_model=CreativeDirectorHandoff,
    status_code=status.HTTP_200_OK,
    summary="Generate complete campaign blueprint from campaign input"
)
async def generate_campaign(input_data: CampaignInput) -> CreativeDirectorHandoff:
    """
    Executes Person 2's LangGraph Creative Director pipeline:
    1. Input Analysis & Strategic Framing
    2. 3-Concept Ideation Engine
    3. Autonomous Decision-Making & Multi-Criteria Rubric Evaluation
    4. Master Strategy & Visual Direction Blueprint (Hex Palette, Typography, Instagram Engine)
    5. Person 3 Handoff Packaging (JSON + Markdown Brief)
    """
    try:
        handoff = autonomous_creative_director.run(input_data)
        return handoff
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign generation failed: {exc}"
        )


@router.post(
    "/generate-from-report",
    response_model=CreativeDirectorHandoff,
    status_code=status.HTTP_200_OK,
    summary="Generate campaign blueprint directly from Person 1 Brand Intelligence Report"
)
async def generate_from_report(request: FromReportRequest) -> CreativeDirectorHandoff:
    """
    Consumes Person 1's BrandIntelligenceReport JSON contract, extracts Brand DNA,
    competitor research, audience pain points, and generates the complete campaign blueprint.
    """
    try:
        handoff = autonomous_creative_director.run_from_person1_report(
            report_data=request.report,
            product_name=request.product_name,
            product_description=request.product_description,
            campaign_objective=request.campaign_objective,
            budget=request.budget
        )
        return handoff
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign generation from Person 1 report failed: {exc}"
        )


@router.get(
    "/outputs",
    summary="List all generated campaign blueprints and briefs in outputs/"
)
async def list_outputs() -> Dict[str, Any]:
    """Lists all saved blueprints in the outputs directory."""
    out_dir = settings.output_dir
    if not out_dir.exists():
        return {"outputs": []}

    files = []
    for p in out_dir.iterdir():
        if p.is_file():
            files.append({
                "filename": p.name,
                "size_bytes": p.stat().st_size,
                "extension": p.suffix
            })
    return {"outputs": files}
