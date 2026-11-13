#!/usr/bin/env python3
"""
CREATIVEIQ · Person 2 — Autonomous Creative Director Agent
==========================================================
Interactive VS Code Terminal Runner & CLI Engine.

Usage in VS Code:
    python run_creative_director.py
    python run_creative_director.py --all
    python run_creative_director.py --brand glowify
    python run_creative_director.py --brand ecoglow
    python run_creative_director.py --brand horizon
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.campaign_schema import CampaignInput, CreativeDirectorHandoff
from app.services.langgraph_creative_director import autonomous_creative_director
from app.core.config import settings


def print_banner():
    banner = """
================================================================================
  CREATIVEIQ  |  Module 02: Autonomous Creative Director Agent (Person 2)
  Campaign Strategy, 3-Concept Ideation & Autonomous Decision-Making Brain
================================================================================
"""
    print(banner)


def print_handoff_summary(handoff: CreativeDirectorHandoff):
    """Prints a beautiful, formatted summary of the campaign blueprint in the terminal."""
    strat = handoff.campaign_strategy
    vd = strat.visual_direction
    ig = strat.platform_strategy

    print("\n" + "=" * 80)
    print(f"  CAMPAIGN BLUEPRINT: {handoff.brand_name.upper()} — \"{strat.campaign_name}\"")
    print("=" * 80)

    print(f"\n[1] CORE STRATEGY")
    print(f"  • Brand & Industry:    {handoff.brand_name} ({handoff.industry})")
    print(f"  • Campaign Name:       {strat.campaign_name}")
    print(f"  • Hero Tagline:        \"{strat.main_tagline}\"")
    print(f"  • Big Creative Idea:   {strat.big_creative_idea}")
    print(f"  • Key Marketing Message: {strat.key_marketing_message}")
    print(f"  • Emotional Shift:     {strat.emotional_positioning}")
    print(f"  • Campaign Objectives: {', '.join(strat.campaign_objectives)}")

    print(f"\n[2] THREE GENERATED CONCEPTS & AUTONOMOUS DECISION MATRIX")
    print("-" * 80)
    print(f"  {'Concept ID & Name':<28} | {'Creat.':<6} | {'Aud.':<6} | {'Brand':<6} | {'Obj.':<6} | {'Overall':<7} | {'Status'}")
    print("-" * 80)

    for e in handoff.concept_evaluations:
        c_obj = next((c for c in handoff.generated_concepts if c.concept_id == e.concept_id), None)
        c_title = f"{e.concept_id}: {c_obj.concept_name if c_obj else ''}"[:26]
        status_str = "WINNER 🏆" if e.selection_status == "selected" else "Rejected"
        print(f"  {c_title:<28} | {e.scores.creativity:<6.1f} | {e.scores.audience_relevance:<6.1f} | {e.scores.brand_consistency:<6.1f} | {e.scores.campaign_objectives_alignment:<6.1f} | {e.overall_score:<7.2f} | {status_str}")

    print("-" * 80)
    print(f"\n[3] AUTONOMOUS SELECTION RATIONALE")
    print(f"  • Winning Concept:     {handoff.selected_concept_id}")
    print(f"  • Executive Verdict:   {handoff.campaign_rationale.selection_verdict}")
    print(f"  • Why Alternatives Lost:")
    for cid, reason in handoff.campaign_rationale.why_selected_over_alternatives.items():
        print(f"      - vs {cid}: {reason}")
    print(f"  • Brand DNA Alignment: {handoff.campaign_rationale.brand_dna_alignment}")
    print(f"  • Competitor Gap Won:  {handoff.campaign_rationale.competitor_white_space}")

    print(f"\n[4] VISUAL DIRECTION BLUEPRINT")
    print(f"  • Design Style:        {vd.design_style}")
    print(f"  • Color Palette:")
    for color in vd.colour_palette:
        print(f"      - {color.color_name:<18} [{color.hex_code}] ({color.role}): {color.psychological_rationale}")
    print(f"  • Headline Font:       {vd.typography_direction.headline_font} ({vd.typography_direction.headline_style_and_vibe})")
    print(f"  • Body Font:           {vd.typography_direction.body_font} ({vd.typography_direction.body_style_and_vibe})")
    print(f"  • Lighting & Mood:     {vd.mood_and_aesthetics}")
    print(f"  • GenAI Image Prompts (Midjourney/Flux):")
    for idx, p in enumerate(vd.midjourney_prompts, start=1):
        print(f"      [{idx}] {p}")

    print(f"\n[5] INSTAGRAM PLATFORM EXECUTION ENGINE")
    print(f"  A. Feed Carousel Post:")
    print(f"     • Headline Hook:    \"{ig.feed_posts.headline_hook}\"")
    print(f"     • Caption Teaser:   \"{ig.feed_posts.caption_body[:120]}...\"")
    print(f"     • CTA:              {ig.feed_posts.call_to_action}")
    print(f"     • Slide Progression: {', '.join(ig.feed_posts.carousel_slide_breakdown[:3])}...")
    print(f"     • Hashtags:         {' '.join(ig.feed_posts.hashtags)}")
    print(f"  B. Stories Sequence:")
    print(f"     • Arc Theme:        {ig.stories.story_arc_theme}")
    print(f"     • Audio Direction:  {ig.stories.sound_and_music_direction}")
    print(f"     • Frames Count:     {len(ig.stories.frames)} frames with interactive stickers")
    print(f"  C. 15-30s Reels / Video Ad:")
    print(f"     • 0-3s Hook:        {ig.advertisements_and_reels.hook_0_to_3s}")
    print(f"     • 3-10s Tension:    {ig.advertisements_and_reels.problem_tension_3_to_10s}")
    print(f"     • 10-20s Solution:  {ig.advertisements_and_reels.solution_product_10_to_20s}")
    print(f"     • 20-30s Climax/CTA: {ig.advertisements_and_reels.climax_cta_20_to_30s}")

    safe_name = handoff.brand_name.lower().replace(" ", "_")
    json_path = settings.output_dir / f"{safe_name}_campaign_blueprint.json"
    md_path = settings.output_dir / f"{safe_name}_creative_brief.md"

    print(f"\n[6] ARTIFACTS PERSISTED FOR PERSON 3")
    print(f"  • Structured JSON Blueprint: {json_path}")
    print(f"  • Markdown Creative Brief:   {md_path}")
    print("=" * 80 + "\n")


# --- PRECONFIGURED TEST BRANDS ---

def run_glowify():
    print("\n>>> Launching Brand 1: GLOWIFY (Clean Skincare — Person 1 Integration)...")
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
                {"statement": "Skin Kindness over Harsh Peels", "evidence_type": "user_provided_information"}
            ],
            "personality": [{"statement": "Empathetic, scientifically honest, calm, unpretentious", "evidence_type": "ai_generated_interpretation"}],
            "tone_of_voice": [{"statement": "Warm, educational, grounded, calming", "evidence_type": "verified_information"}],
            "target_audience": {
                "demographics": [{"statement": "Gen Z and Millennials aged 20-32", "evidence_type": "user_provided_information"}],
                "pain_points": [
                    {"statement": "Overwhelmed by 12-step skincare routines and sensitized skin barriers caused by active acids.", "evidence_type": "verified_information"}
                ]
            }
        },
        "competitor_analysis": {
            "direct_competitors": [{"name": "The Ordinary"}, {"name": "Glossier"}],
            "market_gaps": [{"statement": "White space for gentle, microbiome-friendly barrier repair that feels luxurious yet simple.", "evidence_type": "recommendation"}]
        },
        "strategic_recommendations": [
            {"statement": "Launch an anti-complexity campaign highlighting 'Skin Reset in 3 Steps'.", "evidence_type": "recommendation"}
        ]
    }

    handoff = autonomous_creative_director.run_from_person1_report(
        report_data=person_1_glowify_report,
        product_name="Glowify Barrier Balance Elixir",
        product_description="A microbiome-restoring ceramide serum that reverses barrier damage in 7 days.",
        campaign_objective="Challenge complex 10-step skincare routines and establish Glowify as the #1 barrier-repair authority on Instagram.",
        budget="$35,000"
    )
    print_handoff_summary(handoff)
    return handoff


def run_ecoglow():
    print("\n>>> Launching Brand 2: ECOGLOW (Sustainable Smart Hydration)...")
    ecoglow_input = CampaignInput(
        brand_name="EcoGlow",
        industry="Sustainable Consumer Goods & IoT",
        product_name="EcoGlow Smart Hydration Bottle",
        product_description="An intelligent reusable bottle tracking daily hydration and calculating single-use plastic bottles saved in real time.",
        target_audience="College students, young tech professionals, and gym-goers aged 18-32 focused on personal health and sustainability.",
        campaign_objective="Drive viral awareness of sustainable hydration habits and achieve 3.5x ROAS on Instagram Ads.",
        campaign_objectives=[
            "Increase Brand Awareness by 45%",
            "Drive 25,000 Social Engagements",
            "Achieve 3.5x ROAS on Instagram Direct-to-Consumer Ads"
        ],
        brand_tone="Empowering, Minimalist, High-Energy, Rebellious",
        competitors=["Hydro Flask", "Yeti", "Larq"],
        market_gaps=["Competitors focus on static insulation; EcoGlow highlights quantifiable plastic destruction and gamified hydration habits."],
        campaign_budget="$25,000",
        campaign_duration="30 Days"
    )

    handoff = autonomous_creative_director.run(ecoglow_input)
    print_handoff_summary(handoff)
    return handoff


def run_horizon():
    print("\n>>> Launching Brand 3: HORIZON AI (B2B SaaS Developer Workflow)...")
    horizon_input = CampaignInput(
        brand_name="Horizon AI",
        industry="Enterprise Software & AI Developer Tools",
        product_name="Horizon Autonomous Code Reviewer & PR Copilot",
        product_description="An autonomous AI agent that detects architectural drift, security anti-patterns, and merges pull requests 4x faster.",
        target_audience="VP of Engineering, Lead Architects, and Senior Software Engineers tired of review bottlenecks and alert fatigue.",
        campaign_objective="Generate 500 enterprise sandbox trials and position Horizon as the indispensable pair-programmer for engineering velocity.",
        campaign_objectives=[
            "Drive 500 Enterprise Free Trial Signups",
            "Generate 50,000 Video Views on Instagram & LinkedIn",
            "Establish Authority against Legacy Linters"
        ],
        brand_dna={
            "values": ["Engineering Rigor", "No-Bullshit Velocity", "Zero Hallucination Tolerance"],
            "personality": ["Precise, clever, high-IQ, developer-first"]
        },
        competitors=["SonarQube", "GitHub Copilot", "Snyk"],
        market_gaps=["Competitors spam developers with false positives and useless warnings; developers crave autonomous pull request resolution."],
        campaign_budget="$40,000",
        campaign_duration="45 Days",
        brand_tone="Technical, Witty, Uncompromising Velocity"
    )

    handoff = autonomous_creative_director.run(horizon_input)
    print_handoff_summary(handoff)
    return handoff


def run_custom_interactive():
    print("\n" + "-" * 60)
    print("  INTERACTIVE CAMPAIGN GENERATOR")
    print("-" * 60)
    brand_name = input("Enter Brand Name: ").strip() or "Aura Botanicals"
    industry = input("Enter Industry: ").strip() or "Wellness & Nutrition"
    product_name = input("Enter Product/Service Name: ").strip() or "Aura Adaptogen Energy Droplets"
    product_desc = input("Enter Product Description: ").strip() or "Plant-powered daily adaptogens for crash-free cognitive stamina."
    target_aud = input("Enter Target Audience & Pain Points: ").strip() or "Burned-out startup founders and creatives struggling with afternoon brain fog."
    camp_obj = input("Enter Primary Campaign Objective: ").strip() or "Position Aura as the modern replacement for jittery energy drinks and drive subscription signups."
    budget = input("Enter Budget [e.g. $20,000]: ").strip() or "$20,000"

    c_input = CampaignInput(
        brand_name=brand_name,
        industry=industry,
        product_name=product_name,
        product_description=product_desc,
        target_audience=target_aud,
        campaign_objective=camp_obj,
        campaign_objectives=[
            f"Increase {brand_name} Brand Awareness by 40%",
            "Drive 1,000 Subscription Signups",
            "Achieve > 4.0% Social Engagement"
        ],
        campaign_budget=budget,
        campaign_duration="30 Days",
        brand_tone="Smart, Modern, Calming, High-Efficacy"
    )

    handoff = autonomous_creative_director.run(c_input)
    print_handoff_summary(handoff)
    return handoff


def list_outputs():
    out_dir = settings.output_dir
    print("\n" + "=" * 60)
    print("  GENERATED ARTIFACTS IN outputs/")
    print("=" * 60)
    if not out_dir.exists() or not any(out_dir.iterdir()):
        print("  No outputs found yet.")
        return

    for item in sorted(out_dir.iterdir()):
        size_kb = item.stat().st_size / 1024
        print(f"  • {item.name:<40} ({size_kb:.1f} KB)")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="CREATIVEIQ Person 2 Autonomous Creative Director")
    parser.add_argument("--brand", choices=["glowify", "ecoglow", "horizon"], help="Run specific brand")
    parser.add_argument("--all", action="store_true", help="Run all 3 test brands sequentially")
    parser.add_argument("--list", action="store_true", help="List all generated artifacts in outputs/")
    args = parser.parse_args()

    print_banner()

    if args.brand == "glowify":
        run_glowify()
        return
    elif args.brand == "ecoglow":
        run_ecoglow()
        return
    elif args.brand == "horizon":
        run_horizon()
        return
    elif args.all:
        print("\n>>> EXECUTING ALL 3 TEST BRANDS IN BATCH MODE...")
        run_glowify()
        run_ecoglow()
        run_horizon()
        list_outputs()
        return
    elif args.list:
        list_outputs()
        return

    # Interactive Menu
    while True:
        print("Select an option:")
        print("  [1] Run Brand 1: Glowify (Clean Skincare — Person 1 Integration)")
        print("  [2] Run Brand 2: EcoGlow (Sustainable Smart Hydration)")
        print("  [3] Run Brand 3: Horizon AI (B2B SaaS Developer Tool)")
        print("  [4] Run ALL 3 Brands in Batch Mode")
        print("  [5] Custom Brand (Interactive Input)")
        print("  [6] View Saved Artifacts in outputs/")
        print("  [0] Exit")

        choice = input("\nEnter choice [0-6]: ").strip()
        if choice == "1":
            run_glowify()
        elif choice == "2":
            run_ecoglow()
        elif choice == "3":
            run_horizon()
        elif choice == "4":
            run_glowify()
            run_ecoglow()
            run_horizon()
            list_outputs()
        elif choice == "5":
            run_custom_interactive()
        elif choice == "6":
            list_outputs()
        elif choice in ["0", "q", "exit"]:
            print("\nExiting Creative Director. Good luck with the campaign!")
            break
        else:
            print("Invalid choice, please select between 0 and 6.")


if __name__ == "__main__":
    main()
