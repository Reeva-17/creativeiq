"""Hermetic integration tests for the cross-team workflow contract."""
import pytest
from uuid import uuid4
from app.schemas.brand_input import BrandInput
from app.schemas.brand_report import BrandIntelligenceReport
from app.schemas.campaign_schema import CampaignConcept, CampaignRationale, CreativeDirectorHandoff, MasterCampaignStrategy
from app.schemas.workflow_schema import WorkflowRequest
from app.schemas.workflow_schema import CreativeAsset, WorkflowResponse
from app.services.workflow import run_complete_workflow
from critic_optimizer.schemas.models import CreativeEvaluationResponse


class FakeReportGenerator:
    async def complete(self, brand, competitors):
        return BrandIntelligenceReport(brand_name=brand.brand_name, industry=brand.industry, brand_dna={}, competitor_analysis={}, swot_analysis={}, visual_identity={})


def handoff():
    concept = CampaignConcept(concept_id="CONCEPT_1", concept_name="Clear Choice", main_tagline="Choose clearly.", big_creative_idea="A focused proof-led campaign.", creative_angle="Educational", target_audience_focus="Busy professionals", emotional_positioning="Confident", key_marketing_message="Make the better choice.", unique_angle_vs_competitors="Clear proof.")
    strategy = MasterCampaignStrategy(campaign_name="Clear Choice", selected_concept_id="CONCEPT_1", main_tagline=concept.main_tagline, big_creative_idea=concept.big_creative_idea, target_audience="Busy professionals", emotional_positioning="Confident", key_marketing_message=concept.key_marketing_message)
    return CreativeDirectorHandoff(brand_name="Glowify", industry="Skincare", campaign_name="Clear Choice", selected_concept_id="CONCEPT_1", generated_concepts=[concept], concept_evaluations=[], campaign_rationale=CampaignRationale(selected_concept_id="CONCEPT_1", selection_verdict="Best fit", brand_dna_alignment="Aligned", competitor_white_space="Clear", objective_delivery="Relevant"), campaign_strategy=strategy, creative_brief_markdown="Use clear, confident language.")


@pytest.mark.asyncio
async def test_workflow_passes_context_and_executes_one_bounded_revision(monkeypatch):
    import app.services.workflow as workflow
    class Director:
        def run_from_person1_report(self, report, *args):
            assert report["brand_name"] == "Glowify"
            return handoff()
    prompts, calls = [], []
    def generate_text(prompt):
        prompts.append(prompt)
        return "Draft needs stronger campaign language." if len(prompts) == 1 else "Glowify helps busy professionals make the better choice today."
    def evaluate(request):
        calls.append(request); revision = len(calls) == 1
        return CreativeEvaluationResponse(overall_score=45 if revision else 90, brand_consistency_score=50 if revision else 90, audience_relevance_score=50 if revision else 90, campaign_alignment_score=40 if revision else 90, content_quality_score=80, strengths=[], issues=["Needs brand clarity"] if revision else [], improvement_suggestions=["Mention Glowify and the campaign promise"] if revision else [], status="needs_revision" if revision else "approved")
    monkeypatch.setattr(workflow, "autonomous_creative_director", Director())
    monkeypatch.setattr(workflow, "generate_marketing_text", generate_text)
    monkeypatch.setattr(workflow, "_evaluate", evaluate)
    result = await run_complete_workflow(WorkflowRequest(brand=BrandInput(brand_name="Glowify", industry="Skincare")), FakeReportGenerator())
    assert len(result.creative_assets) == len(result.evaluations) == 2
    assert result.final_status == "approved"
    assert result.creative_assets[0].image_url is None
    assert result.creative_assets[0].poster_url is None
    assert "Revision feedback from the campaign critic" in prompts[1]
    assert calls[0].campaign_goal == "Make the better choice."


@pytest.mark.asyncio
async def test_workflow_does_not_loop_when_disabled(monkeypatch):
    import app.services.workflow as workflow
    monkeypatch.setattr(workflow, "autonomous_creative_director", type("D", (), {"run_from_person1_report": lambda *_: handoff()})())
    monkeypatch.setattr(workflow, "generate_marketing_text", lambda _: "Short draft.")
    monkeypatch.setattr(workflow, "_evaluate", lambda _: CreativeEvaluationResponse(overall_score=20, brand_consistency_score=20, audience_relevance_score=20, campaign_alignment_score=20, content_quality_score=80, strengths=[], issues=["Weak"], improvement_suggestions=["Improve"], status="needs_revision"))
    result = await run_complete_workflow(WorkflowRequest(brand=BrandInput(brand_name="Glowify", industry="Skincare"), max_revisions=0), FakeReportGenerator())
    assert len(result.creative_assets) == 1


def test_workflow_http_endpoint_returns_the_combined_contract(monkeypatch):
    """Exercise FastAPI validation/serialization without contacting an AI provider."""
    from fastapi.testclient import TestClient
    from app.api.dependencies import get_report_generator
    from app.main import app
    import app.api.routes.workflow as workflow_route

    report = FakeReportGenerator()
    expected = WorkflowResponse(
        campaign_id=uuid4(),
        brand_intelligence=BrandIntelligenceReport(
            brand_name="Glowify", industry="Skincare", brand_dna={},
            competitor_analysis={}, swot_analysis={}, visual_identity={},
        ),
        campaign_handoff=handoff(),
        creative_assets=[CreativeAsset(text="Glowify campaign copy.")],
        evaluations=[],
        final_status="approved",
    )

    async def fake_workflow(request, generator):
        assert request.brand.brand_name == "Glowify"
        assert generator is report
        return expected

    monkeypatch.setattr(workflow_route, "run_complete_workflow", fake_workflow)
    app.dependency_overrides[get_report_generator] = lambda: report
    try:
        response = TestClient(app).post(
            "/api/v1/workflow/run",
            json={"brand": {"brand_name": "Glowify", "industry": "Skincare"}},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["campaign_handoff"]["brand_name"] == "Glowify"


@pytest.mark.asyncio
async def test_workflow_creates_a_poster_only_from_a_generated_image(monkeypatch, tmp_path):
    import app.services.workflow as workflow

    monkeypatch.setattr(workflow, "autonomous_creative_director", type("D", (), {"run_from_person1_report": lambda *_: handoff()})())
    monkeypatch.setattr(workflow, "generate_marketing_text", lambda _: "Glowify campaign copy.")
    monkeypatch.setattr(workflow, "_evaluate", lambda _: CreativeEvaluationResponse(overall_score=90, brand_consistency_score=90, audience_relevance_score=90, campaign_alignment_score=90, content_quality_score=90, strengths=[], issues=[], improvement_suggestions=[], status="approved"))
    image_path = tmp_path / "image.png"
    poster_path = tmp_path / "poster.png"
    monkeypatch.setattr(workflow, "generate_image", lambda _: image_path)
    captured = {}
    def make_poster(**kwargs):
        captured.update(kwargs)
        return poster_path
    monkeypatch.setattr(workflow, "generate_poster", make_poster)

    result = await run_complete_workflow(
        WorkflowRequest(brand=BrandInput(brand_name="Glowify", industry="Skincare"), generate_poster=True),
        FakeReportGenerator(),
    )
    assert result.creative_assets[0].image_url == "/generated/image.png"
    assert result.creative_assets[0].poster_url == "/generated/poster.png"
    assert captured["image_path"] == image_path


def test_image_prompt_is_compact_and_uses_campaign_visual_direction():
    from app.services.workflow import _image_prompt
    prompt = _image_prompt(handoff())
    assert len(prompt) <= 2048
    assert "Glowify" in prompt
    assert "no lettering" in prompt
