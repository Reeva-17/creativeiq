from critic_optimizer.schemas.models import (
    CreativeEvaluationResponse
)


def create_revision_feedback(
    creative_text: str,
    evaluation: CreativeEvaluationResponse
):
    if evaluation.status == "approved":
        return {
            "approved": True,
            "message": "Creative approved. No revision needed."
        }

    return {
        "approved": False,
        "original_creative": creative_text,
        "score": evaluation.overall_score,
        "issues": evaluation.issues,
        "revision_instructions": evaluation.improvement_suggestions,
        "message": "Revise the creative using the feedback above."
    }