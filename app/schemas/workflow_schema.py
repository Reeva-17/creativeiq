"""Contracts for the complete four-agent workflow.

The nested report/handoff fields deliberately retain each agent's output.  This
makes the handoffs inspectable and prevents later agents from silently replacing
the brand context supplied by earlier agents.
"""
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.schemas.brand_input import BrandInput
from app.schemas.brand_report import BrandIntelligenceReport
from app.schemas.campaign_schema import CreativeDirectorHandoff
from critic_optimizer.schemas.models import CreativeEvaluationResponse


class WorkflowRequest(BaseModel):
    campaign_id: UUID = Field(default_factory=uuid4)
    brand: BrandInput
    competitor_names: list[str] = Field(default_factory=list, max_length=15)
    product_name: str | None = None
    product_description: str | None = None
    campaign_objective: str | None = None
    campaign_budget: str | None = None
    campaign_duration: str = "30 Days"
    # Images use a separate paid/provider credential and are intentionally opt-in.
    generate_image: bool = False
    # A poster is composed from the real generated image using the selected
    # campaign messaging; enabling it also generates the required image.
    generate_poster: bool = False
    # One revision is the maximum supported feedback cycle; this bounds execution.
    max_revisions: int = Field(default=1, ge=0, le=1)


class CreativeAsset(BaseModel):
    text: str
    image_url: str | None = None
    poster_url: str | None = None
    revision_number: int = 0


class AgentExecutionStatus(BaseModel):
    agent: str
    status: str
    detail: str


class WorkflowResponse(BaseModel):
    campaign_id: UUID
    brand_intelligence: BrandIntelligenceReport
    campaign_handoff: CreativeDirectorHandoff
    creative_assets: list[CreativeAsset]
    evaluations: list[CreativeEvaluationResponse]
    revision_feedback: list[dict[str, Any]] = Field(default_factory=list)
    agent_statuses: list[AgentExecutionStatus] = Field(default_factory=list)
    final_status: str


class PromptWorkflowRequest(BaseModel):
    """One-prompt public intake for the browser experience."""
    prompt: str = Field(min_length=20, max_length=6000)
    generate_poster: bool = True
    max_revisions: int = Field(default=1, ge=0, le=1)
