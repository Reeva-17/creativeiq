from enum import Enum
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    verified = "verified_information"
    user_provided = "user_provided_information"
    ai_interpretation = "ai_generated_interpretation"
    recommendation = "recommendation"
    unavailable = "unavailable"


class Finding(BaseModel):
    statement: str
    evidence_type: EvidenceType
    rationale: str | None = None
    source_urls: list[str] = Field(default_factory=list)


class AudienceProfile(BaseModel):
    demographics: list[Finding] = Field(default_factory=list)
    psychographics: list[Finding] = Field(default_factory=list)
    pain_points: list[Finding] = Field(default_factory=list)
    motivations: list[Finding] = Field(default_factory=list)


class BrandDNA(BaseModel):
    identity: list[Finding] = Field(default_factory=list)
    personality: list[Finding] = Field(default_factory=list)
    positioning: Finding | None = None
    mission: Finding | None = None
    vision: Finding | None = None
    values: list[Finding] = Field(default_factory=list)
    target_audience: AudienceProfile = Field(default_factory=AudienceProfile)
    tone_of_voice: list[Finding] = Field(default_factory=list)
    communication_style: list[Finding] = Field(default_factory=list)
    usp: Finding | None = None
    differentiators: list[Finding] = Field(default_factory=list)
    strengths: list[Finding] = Field(default_factory=list)
    weaknesses: list[Finding] = Field(default_factory=list)
    opportunities: list[Finding] = Field(default_factory=list)


class CompetitorProfile(BaseModel):
    name: str
    category: str  # direct or indirect
    positioning: Finding | None = None
    products_services: list[Finding] = Field(default_factory=list)
    target_audience: list[Finding] = Field(default_factory=list)
    communication_style: list[Finding] = Field(default_factory=list)
    usps: list[Finding] = Field(default_factory=list)
    strengths: list[Finding] = Field(default_factory=list)
    weaknesses: list[Finding] = Field(default_factory=list)
    research_status: str
    source_urls: list[str] = Field(default_factory=list)


class CompetitorAnalysis(BaseModel):
    direct_competitors: list[CompetitorProfile] = Field(default_factory=list)
    indirect_competitors: list[CompetitorProfile] = Field(default_factory=list)
    comparison: list[Finding] = Field(default_factory=list)
    market_gaps: list[Finding] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class SWOTAnalysis(BaseModel):
    strengths: list[Finding] = Field(default_factory=list)
    weaknesses: list[Finding] = Field(default_factory=list)
    opportunities: list[Finding] = Field(default_factory=list)
    threats: list[Finding] = Field(default_factory=list)


class VisualIdentity(BaseModel):
    suggested_colors: list[Finding] = Field(default_factory=list)
    typography: Finding | None = None
    visual_direction: Finding | None = None


class BrandIntelligenceReport(BaseModel):
    """Versioned, provider-agnostic contract for downstream agents."""
    schema_version: str = "1.0.0"
    brand_name: str
    industry: str
    executive_summary: list[Finding] = Field(default_factory=list)
    brand_overview: list[Finding] = Field(default_factory=list)
    brand_dna: BrandDNA
    competitor_analysis: CompetitorAnalysis
    swot_analysis: SWOTAnalysis
    visual_identity: VisualIdentity
    marketing_insights: list[Finding] = Field(default_factory=list)
    strategic_recommendations: list[Finding] = Field(default_factory=list)
    key_takeaways: list[Finding] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
