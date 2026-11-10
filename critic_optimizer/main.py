from fastapi import FastAPI, HTTPException

from critic_optimizer.schemas.models import (
    CreativeEvaluationRequest,
    CreativeEvaluationResponse
)

from critic_optimizer.services.critic import evaluate_creative

from critic_optimizer.services.feedback_service import (
    create_revision_feedback
)

from critic_optimizer.services.ai_critic import evaluate_with_ai

app = FastAPI(
    title="CreativeIQ Critic & Optimizer API",
    description="Evaluates marketing creatives and provides improvement feedback.",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "CreativeIQ Critic & Optimizer is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "critic_optimizer"
    }


@app.post("/evaluate")
def evaluate(request: CreativeEvaluationRequest):
    try:
        try:
            result = evaluate_with_ai(request)
            print("Evaluation completed using Gemini AI.")
        except Exception as e:
            print(f"Gemini unavailable. Using basic evaluator. Reason: {e}")
            result = evaluate_creative(request)

        feedback = create_revision_feedback(request.creative_text, result)
        return {
            "evaluation": result,
            "feedback": feedback
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )