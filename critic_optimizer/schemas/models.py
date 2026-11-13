from pydantic import BaseModel, Field
from typing import Optional, List


class CreativeEvaluationRequest(BaseModel):
    brand_name: str
    target_audience: str
    brand_tone: str
    campaign_goal: str

    creative_text: str
    image_url: Optional[str] = None


class CreativeEvaluationResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100)

    brand_consistency_score: int
    audience_relevance_score: int
    campaign_alignment_score: int
    content_quality_score: int

    strengths: List[str]
    issues: List[str]
    improvement_suggestions: List[str]

    status: str
