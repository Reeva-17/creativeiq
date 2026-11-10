import sys
import os
import json
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
from app.services.langgraph_creative_director import autonomous_creative_director


def test_glowify_person1_integration():
    """Test Brand 1: Glowify using Person 1 Brand Intelligence Report integration."""
    print("\n" + "=" * 60)
    print("TEST 1: PERSON 1 INTEGRATION — GLOWIFY (SKINCARE)")
    print("=" * 60)

    # Simulated full Person 1 BrandIntelligenceReport v1.0.0 for Glowify
    person_1_glowify_report = {
        "schema_version": "1.0.0",
        "brand_name": "Glowify",
        "industry": "Clean Skincare & Dermacosmetics",
        "executive_summary": [
            {"statement": "Glowify is a transparent, barrier-repair skincare brand for young adults suffering from skin fatigue and over-exfoliation.", "evidence_type": "verified_information"}
        ],
        "brand_dna": {
            "values": [
                {"statement": "Radical Formulation Transparency", "evidence_type": "user_provided_information"},
                {"statement": "Skin Kindness over Harsh Peels", "evidence_type": "user_provided_information"},
                {"statement": "Accessible Daily Luxury", "evidence_type": "user_provided_information"}
            ],
            "personality": [
                {"statement": "Empathetic, scientifically honest, calm, unpretentious", "evidence_type": "ai_generated_interpretation"}
            ],
            "tone_of_voice": [
                {"statement": "Warm, educational, grounded, calming", "evidence_type": "verified_information"}
            ],
            "target_audience": {
                "demographics": [
                    {"statement": "Gen Z and Millennials aged 20-32, urban dwellers", "evidence_type": "user_provided_information"}
                ],
                "pain_points": [
                    {"statement": "Overwhelmed by 12-step skincare routines and sensitized skin barriers caused by harsh active acids.", "evidence_type": "verified_information"},
                    {"statement": "Cynical about exaggerated influencer filter results and expensive celebrity cosmetic lines.", "evidence_type": "ai_generated_interpretation"}
                ]
            }
        },
        "competitor_analysis": {
            "direct_competitors": [
                {"name": "The Ordinary"},
                {"name": "Glossier"},
                {"name": "Cerave"}
            ],
            "market_gaps": [
                {"statement": "White space for gentle, microbiome-friendly barrier repair that doesn't feel clinical or boring.", "evidence_type": "recommendation"}
            ]
        },
        "strategic_recommendations": [
            {"statement": "Launch an anti-complexity campaign highlighting 'Skin Reset in 3 Steps'.", "evidence_type": "recommendation"},
            {"statement": "Drive TikTok/Instagram community conversations debunking skin-barrier damage.", "evidence_type": "recommendation"}
        ]
    }

    result = autonomous_creative_director.run_from_person1_report(
        report_data=person_1_glowify_report,
        product_name="Glowify Barrier Balance Elixir",
        product_description="A microbiome-restoring ceramide serum that reverses barrier damage in 7 days.",
        campaign_objective="Challenge complex 10-step skincare routines and establish Glowify as the #1 barrier-repair authority on Instagram.",
        budget="$35,000"
    )

    print("\n[GLOWIFY RESULT]")
    print(f"Campaign Name: {result.campaign_name}")
    print(f"Tagline: {result.campaign_strategy.main_tagline}")
    print(f"Winning Concept ID: {result.selected_concept_id}")
    print(f"Big Idea: {result.campaign_strategy.big_creative_idea}")
    print(f"Color Palette: {[c.color_name + ' (' + c.hex_code + ')' for c in result.campaign_strategy.visual_direction.colour_palette]}")
    print(f"Instagram Post Hook: {result.campaign_strategy.platform_strategy.feed_posts.headline_hook}")

    assert result.brand_name == "Glowify"
    assert len(result.generated_concepts) == 3
    assert len(result.concept_evaluations) == 3
    assert result.selected_concept_id in ["CONCEPT_1", "CONCEPT_2", "CONCEPT_3"]
    print("PASS: Glowify Person 1 integration test succeeded!")


def test_horizon_ai_b2b_saas():
    """Test Brand 3: Horizon AI (B2B SaaS / Developer Workflow Productivity)."""
    print("\n" + "=" * 60)
    print("TEST 3: B2B AGENTIC WORKFLOW — HORIZON AI")
    print("=" * 60)

    horizon_input = CampaignInput(
        brand_name="Horizon AI",
        industry="Enterprise Software & AI Developer Tools",
        product_name="Horizon Autonomous Code Reviewer & PR Copilot",
        product_description="An autonomous AI agent that detects architectural drift, security anti-patterns, and merges pull requests 4x faster.",
        target_audience="Engineering leaders, VP of Engineering, Lead Architects, and Senior Software Engineers tired of review bottlenecks.",
        campaign_objective="Generate 500 enterprise sandbox trials and position Horizon as the indispensable pair-programmer for engineering velocity.",
        campaign_objectives=[
            "Drive 500 Enterprise Free Trial Signups",
            "Generate 50,000 LinkedIn & Instagram Video Views",
            "Establish Authority against Legacy Linters"
        ],
        brand_dna={
            "values": ["Engineering Rigor", "No-Bullshit Velocity", "Zero Hallucination Tolerance"],
            "personality": ["Precise, clever, high-IQ, developer-first"],
            "tone": ["Witty, intellectually honest, technical yet accessible"]
        },
        competitors=["SonarQube", "GitHub Copilot", "Snyk"],
        market_gaps=["Competitors spam developers with false positives and useless warnings; developers crave autonomous pull request resolution."],
        campaign_platforms=["Instagram Reels", "Instagram Carousel Infographics", "Instagram Stories"],
        campaign_budget="$40,000",
        campaign_duration="45 Days",
        brand_tone="Technical, Witty, Uncompromising Velocity"
    )

    result = autonomous_creative_director.run(horizon_input)

    print("\n[HORIZON AI RESULT]")
    print(f"Campaign Name: {result.campaign_name}")
    print(f"Tagline: {result.campaign_strategy.main_tagline}")
    print(f"Winning Concept ID: {result.selected_concept_id}")
    print(f"Selected Concept Rationale: {result.campaign_rationale.selection_verdict[:200]}...")
    print(f"Headline Font: {result.campaign_strategy.visual_direction.typography_direction.headline_font}")
    print(f"Midjourney Prompts Count: {len(result.campaign_strategy.visual_direction.midjourney_prompts)}")

    assert result.brand_name == "Horizon AI"
    assert len(result.generated_concepts) == 3
    assert len(result.concept_evaluations) == 3
    print("PASS: Horizon AI B2B SaaS test succeeded!")


if __name__ == "__main__":
    test_glowify_person1_integration()
    test_horizon_ai_b2b_saas()
