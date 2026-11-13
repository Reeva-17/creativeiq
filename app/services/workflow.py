"""The application-level orchestration for Persons 1--4.

LangGraph remains responsible for Person 2's internal strategy workflow.  This
service connects that result to the existing Person 3 and Person 4 services and
limits the return loop to one revision.
"""
from app.schemas.workflow_schema import AgentExecutionStatus, CreativeAsset, WorkflowRequest, WorkflowResponse
from app.services.report_generator import ReportGenerator
from app.services.langgraph_creative_director import autonomous_creative_director
from creative_generation.services.text_generator import generate_marketing_text
from creative_generation.services.image_generator import generate_image
from creative_generation.services.poster_generator import generate_poster
from critic_optimizer.schemas.models import CreativeEvaluationRequest
from critic_optimizer.services.critic import evaluate_creative
from critic_optimizer.services.ai_critic import evaluate_with_ai
from critic_optimizer.services.feedback_service import create_revision_feedback


class WorkflowAgentError(RuntimeError):
    """Preserves the failed agent identity for API clients and the browser UI."""

    def __init__(self, agent: str, cause: Exception):
        self.agent = agent
        super().__init__(str(cause))


def _creative_context(handoff, feedback: dict | None = None) -> str:
    """Build Person 3's prompt from the actual Person 1/2 handoff."""
    strategy = handoff.campaign_strategy
    context = f"""Brand: {handoff.brand_name}
Industry: {handoff.industry}
Campaign: {strategy.campaign_name}
Tagline: {strategy.main_tagline}
Big idea: {strategy.big_creative_idea}
Audience: {strategy.target_audience}
Message: {strategy.key_marketing_message}
Creative brief:\n{handoff.creative_brief_markdown}"""
    if feedback:
        context += "\nRevision feedback from the campaign critic:\n" + "\n".join(feedback.get("revision_instructions", []))
    return context


def _image_prompt(handoff) -> str:
    """Create a compact FLUX-safe visual brief from the real Person 1/2 handoff.

    FLUX.1 Schnell accepts a prompt of at most 2,048 characters. The full
    Markdown creative brief is deliberately much longer, so passing it directly
    caused Cloudflare to reject otherwise valid requests.
    """
    strategy = handoff.campaign_strategy
    visual = strategy.visual_direction
    palette = ", ".join(f"{item.color_name} ({item.hex_code})" for item in visual.colour_palette[:4])
    prompt = (
        f"Premium social-media advertising image for {handoff.brand_name}, {handoff.industry}. "
        f"Campaign: {strategy.campaign_name}. Core idea: {strategy.big_creative_idea}. "
        f"Audience: {strategy.target_audience}. Visual style: {visual.design_style}. "
        f"Mood: {visual.mood_and_aesthetics}. Palette: {palette}. "
        "Create a polished commercial composition with a clear focal subject, room for a later text overlay, "
        "and no lettering, logo, watermark, or embedded typography."
    )
    return prompt[:2048]


def _evaluate(request: CreativeEvaluationRequest):
    """Prefer the configured AI critic; retain the existing transparent local fallback."""
    try:
        return evaluate_with_ai(request)
    except Exception:
        return evaluate_creative(request)


async def run_complete_workflow(request: WorkflowRequest, report_generator: ReportGenerator) -> WorkflowResponse:
    statuses: list[AgentExecutionStatus] = []
    # Person 1: use the same generator as the public brand endpoint, including its
    # dependency-injected provider for testability.
    try:
        report = await report_generator.complete(request.brand, request.competitor_names)
    except Exception as exc:
        raise WorkflowAgentError("Person 1 · Brand Intelligence", exc) from exc
    statuses.append(AgentExecutionStatus(agent="Person 1 · Brand Intelligence", status="completed", detail="Created Brand DNA, competitor context, and SWOT report."))

    # Person 2: adapter consumes the full, versioned Person 1 report.
    try:
        handoff = autonomous_creative_director.run_from_person1_report(
            report.model_dump(mode="json"), request.product_name, request.product_description,
            request.campaign_objective, request.campaign_budget, request.campaign_duration,
        )
    except Exception as exc:
        raise WorkflowAgentError("Person 2 · Creative Director", exc) from exc
    statuses.append(AgentExecutionStatus(agent="Person 2 · Creative Director", status="completed", detail="Created campaign strategy and structured creative brief."))
    strategy = handoff.campaign_strategy
    tone = ", ".join(request.brand.brand_values) or "brand-appropriate, clear and consistent"

    # Person 3: no local placeholder is substituted if Gemini is unavailable.
    try:
        creative_text = generate_marketing_text(_creative_context(handoff))
    except Exception as exc:
        raise WorkflowAgentError("Person 3 · Creative Generator", exc) from exc
    image_url = None
    poster_url = None
    # Poster composition requires a real background image, so requesting a
    # poster implicitly requests the Cloudflare image generation step.
    if request.generate_image or request.generate_poster:
        try:
            image = generate_image(_image_prompt(handoff))
        except Exception as exc:
            raise WorkflowAgentError("Person 3 · Creative Generator", exc) from exc
        image_url = f"/generated/{image.name}"
        if request.generate_poster:
            feed_post = strategy.platform_strategy.feed_posts
            try:
                poster = generate_poster(
                    image_path=image,
                    brand_name=handoff.brand_name,
                    headline=strategy.main_tagline,
                    offer=request.product_name or strategy.key_marketing_message,
                    cta=feed_post.call_to_action,
                )
            except Exception as exc:
                raise WorkflowAgentError("Person 3 · Creative Generator", exc) from exc
            poster_url = f"/generated/{poster.name}"
    assets = [CreativeAsset(text=creative_text, image_url=image_url, poster_url=poster_url)]
    statuses.append(AgentExecutionStatus(agent="Person 3 · Creative Generator", status="completed", detail="Generated marketing copy" + (", image, and poster." if poster_url else ".")))

    # Person 4 receives both the actual strategy and generated asset.
    critic_input = CreativeEvaluationRequest(
        brand_name=request.brand.brand_name,
        target_audience=strategy.target_audience,
        brand_tone=tone,
        campaign_goal=strategy.key_marketing_message,
        creative_text=creative_text,
        image_url=image_url,
    )
    try:
        evaluation = _evaluate(critic_input)
    except Exception as exc:
        raise WorkflowAgentError("Person 4 · Critic & Optimizer", exc) from exc
    evaluations = [evaluation]
    feedback_items: list[dict] = []

    # Bounded Person 4 -> Person 3 loop.  The revision is a new real LLM request
    # carrying the critic's actionable instructions, then it is evaluated again.
    if evaluation.status == "needs_revision" and request.max_revisions:
        feedback = create_revision_feedback(creative_text, evaluation)
        feedback_items.append(feedback)
        try:
            revised_text = generate_marketing_text(_creative_context(handoff, feedback))
        except Exception as exc:
            raise WorkflowAgentError("Person 3 · Creative Generator (revision)", exc) from exc
        assets.append(CreativeAsset(text=revised_text, image_url=image_url, poster_url=poster_url, revision_number=1))
        try:
            evaluations.append(_evaluate(critic_input.model_copy(update={"creative_text": revised_text})))
        except Exception as exc:
            raise WorkflowAgentError("Person 4 · Critic & Optimizer (revision)", exc) from exc

    statuses.append(AgentExecutionStatus(agent="Person 4 · Critic & Optimizer", status="completed", detail="Evaluated creative" + (" and evaluated one revision." if feedback_items else ".")))

    return WorkflowResponse(
        campaign_id=request.campaign_id,
        brand_intelligence=report,
        campaign_handoff=handoff,
        creative_assets=assets,
        evaluations=evaluations,
        revision_feedback=feedback_items,
        agent_statuses=statuses,
        final_status=evaluations[-1].status,
    )
