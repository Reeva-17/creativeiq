import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.campaign_schema import CampaignInput
from app.services.campaign_agent import campaign_agent


def test_campaign_agent():

    print("\nCREATIVEIQ CAMPAIGN AGENT TEST")
    print("=" * 50)

    campaign = CampaignInput(
        brand_name="EcoGlow",
        product_name="EcoGlow Smart Bottle",
        product_description=(
            "A reusable smart water bottle designed "
            "to encourage sustainable hydration."
        ),
        target_audience=(
            "College students and young working professionals "
            "aged 18-30."
        ),
        campaign_objective=(
            "Increase brand awareness and encourage "
            "sustainable hydration habits."
        ),
        campaign_platforms=[
            "Instagram",
            "YouTube",
            "LinkedIn"
        ],
        campaign_budget="$50,000",
        campaign_duration="30 days",
        brand_tone="Modern, youthful, sustainable",
        key_messages=[
            "Reduce single-use plastic",
            "Build sustainable hydration habits"
        ],
        competitors=[
            "Traditional reusable bottle brands"
        ],
        additional_requirements=(
            "Focus on digital-first marketing campaigns."
        )
    )

    print("\nGenerating campaign...")

    result = campaign_agent.generate_campaign(campaign)

    print("\nTHREE GENERATED CONCEPTS")

    for concept in result.generated_concepts:
        print(f"\n{concept.concept_id}: {concept.concept_name}")
        print(f"Tagline: {concept.main_tagline}")

    print("\nCONCEPT EVALUATIONS")

    for evaluation in result.concept_evaluations:
        print(
            evaluation.concept_id,
            evaluation.overall_score,
            evaluation.selection_status
        )

    print("\nSELECTED CONCEPT")
    print(result.selected_concept_id)

    print("\nSELECTION REASON")
    print(result.campaign_rationale.selection_verdict)

    print("\nFINAL CAMPAIGN STRATEGY")
    print(result.campaign_strategy.model_dump_json(indent=2))

    print("\nCOMPLETE JSON OUTPUT")
    print(result.model_dump_json(indent=2))

    print("\nCAMPAIGN AGENT TEST PASSED!")


if __name__ == "__main__":
    test_campaign_agent()
