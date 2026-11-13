import json
from critic_optimizer.ai.gemini_provider import generate_ai_evaluation
from critic_optimizer.schemas.models import (
    CreativeEvaluationRequest,
    CreativeEvaluationResponse
)


def evaluate_with_ai(request: CreativeEvaluationRequest) -> CreativeEvaluationResponse:

    prompt = f"""
You are an expert marketing creative evaluator.

Evaluate the following campaign creative.

Brand: {request.brand_name}
Target Audience: {request.target_audience}
Brand Tone: {request.brand_tone}
Campaign Goal: {request.campaign_goal}
Creative Text: {request.creative_text}

Evaluate these four dimensions:
1. Brand consistency (0-100)
2. Audience relevance (0-100)
3. Campaign alignment (0-100)
4. Content quality (0-100)

Give more importance to brand consistency and campaign alignment.

Return ONLY valid JSON in exactly this format:

{{
    "brand_consistency_score": 0,
    "audience_relevance_score": 0,
    "campaign_alignment_score": 0,
    "content_quality_score": 0,
    "strengths": [],
    "issues": [],
    "improvement_suggestions": []
}}

Be honest and specific. Do not give high scores without justification.
"""

    response_text = generate_ai_evaluation(prompt)

    data = json.loads(response_text)

    brand = max(0, min(100, int(data["brand_consistency_score"])))
    audience = max(0, min(100, int(data["audience_relevance_score"])))
    campaign = max(0, min(100, int(data["campaign_alignment_score"])))
    quality = max(0, min(100, int(data["content_quality_score"])))

    overall = round(
        brand * 0.30 +
        audience * 0.25 +
        campaign * 0.30 +
        quality * 0.15
    )

    return CreativeEvaluationResponse(
        overall_score=overall,
        brand_consistency_score=brand,
        audience_relevance_score=audience,
        campaign_alignment_score=campaign,
        content_quality_score=quality,
        strengths=data.get("strengths", []),
        issues=data.get("issues", []),
        improvement_suggestions=data.get("improvement_suggestions", []),
        status="approved" if overall >= 70 else "needs_revision"
    )
