import re

from critic_optimizer.schemas.models import (
    CreativeEvaluationRequest,
    CreativeEvaluationResponse
)


def get_words(text: str) -> set:
    """Convert text into lowercase keywords."""
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def calculate_relevance(reference: str, creative: str) -> int:
    """Measure keyword overlap between requirements and creative."""
    reference_words = get_words(reference)
    creative_words = get_words(creative)

    if not reference_words:
        return 50

    overlap = reference_words.intersection(creative_words)
    score = int((len(overlap) / len(reference_words)) * 100)

    return min(score, 100)


def evaluate_creative(
    request: CreativeEvaluationRequest
) -> CreativeEvaluationResponse:

    text = request.creative_text.strip()

    # 1. Brand consistency
    brand_reference = (
        request.brand_name + " " + request.brand_tone
    )
    brand_score = calculate_relevance(brand_reference, text)

    # 2. Audience relevance
    audience_score = calculate_relevance(
        request.target_audience, text
    )

    # 3. Campaign alignment
    campaign_score = calculate_relevance(
        request.campaign_goal, text
    )

    # 4. Content quality: basic rule-based checks
    quality_score = 100
    issues = []
    suggestions = []
    strengths = []

    if len(text) < 20:
        quality_score -= 25
        issues.append("Creative text is too short.")
        suggestions.append(
            "Add more meaningful content to communicate the message."
        )

    if len(text) > 300:
        quality_score -= 15
        issues.append("Creative text may be too lengthy.")
        suggestions.append(
            "Make the message more concise and impactful."
        )

    if not re.search(r"[.!?]$", text):
        quality_score -= 10
        issues.append("The message lacks closing punctuation.")
        suggestions.append(
            "Improve sentence structure and punctuation."
        )

    if len(get_words(text)) < 5:
        quality_score -= 20
        issues.append("The creative has very limited vocabulary.")
        suggestions.append(
            "Add more descriptive and engaging words."
        )

    quality_score = max(0, quality_score)

    # Identify strengths
    if brand_score >= 60:
        strengths.append("Good brand keyword alignment.")

    if audience_score >= 60:
        strengths.append("Relevant to the target audience.")

    if campaign_score >= 60:
        strengths.append("Aligned with the campaign goal.")

    if quality_score >= 80:
        strengths.append("Good basic content structure.")

    # Overall weighted score
    overall_score = round(
        brand_score * 0.30
        + audience_score * 0.25
        + campaign_score * 0.30
        + quality_score * 0.15
    )

    if brand_score < 60:
        issues.append("Weak brand alignment.")
        suggestions.append(
            "Include language that better reflects the brand tone."
        )

    if audience_score < 50:
        issues.append("Weak target audience relevance.")
        suggestions.append(
            "Adapt the message to the interests of the target audience."
        )

    if campaign_score < 50:
        issues.append("Weak campaign goal alignment.")
        suggestions.append(
            "Make the campaign's main objective clearer."
        )

    # Final decision
    status = "approved" if overall_score >= 70 else "needs_revision"

    if not issues:
        suggestions.append(
            "Creative meets the basic evaluation criteria."
        )

    return CreativeEvaluationResponse(
        overall_score=overall_score,
        brand_consistency_score=brand_score,
        audience_relevance_score=audience_score,
        campaign_alignment_score=campaign_score,
        content_quality_score=quality_score,
        strengths=strengths,
        issues=issues,
        improvement_suggestions=suggestions,
        status=status
    )