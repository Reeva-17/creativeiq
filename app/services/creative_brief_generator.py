from typing import List
from app.schemas.campaign_schema import (
    CampaignInput,
    CampaignConcept,
    ConceptEvaluation,
    CampaignRationale,
    MasterCampaignStrategy
)


def generate_markdown_creative_brief(
    campaign_input: CampaignInput,
    concepts: List[CampaignConcept],
    evaluations: List[ConceptEvaluation],
    rationale: CampaignRationale,
    strategy: MasterCampaignStrategy
) -> str:
    """
    Generate an executive-ready Markdown Creative Brief summarizing all decisions,
    visual direction, concept comparisons, and platform strategies for Person 3.
    """
    winning_concept = next(
        (c for c in concepts if c.concept_id == rationale.selected_concept_id),
        concepts[0]
    )

    # Color Palette Markdown Table
    color_rows = []
    for c in strategy.visual_direction.colour_palette:
        color_rows.append(f"| **{c.color_name}** | `{c.hex_code}` | {c.role} | {c.psychological_rationale} |")
    colors_table = "\n".join(color_rows)

    # Concept Evaluations Table
    eval_rows = []
    for e in evaluations:
        status_badge = "🏆 **SELECTED**" if e.selection_status == "selected" else "❌ Rejected"
        concept_obj = next((c for c in concepts if c.concept_id == e.concept_id), None)
        c_name = concept_obj.concept_name if concept_obj else e.concept_id
        eval_rows.append(
            f"| `{e.concept_id}`: {c_name} | {e.scores.creativity}/10 | {e.scores.audience_relevance}/10 | "
            f"{e.scores.brand_consistency}/10 | {e.scores.campaign_objectives_alignment}/10 | "
            f"**{e.overall_score}/10** | {status_badge} |"
        )
    eval_table = "\n".join(eval_rows)

    # Midjourney Prompts
    mj_prompts = "\n".join([f"- `{p}`" for p in strategy.visual_direction.midjourney_prompts])

    # Instagram Story Frames
    story_frames_md = "\n".join([
        f"  - **Frame {f.frame_number}**: {f.visual_scene} *(Copy: \"{f.overlay_copy}\" | Interactive: {f.interactive_sticker})*"
        for f in strategy.platform_strategy.stories.frames
    ])

    # Carousel Slide Breakdown
    carousel_slides_md = "\n".join([f"  - {s}" for s in strategy.platform_strategy.feed_posts.carousel_slide_breakdown])

    # Roadmap
    roadmap_md = "\n".join([
        f"- **{phase.phase_name}** ({phase.timeline}): {', '.join(phase.key_activities)}"
        for phase in strategy.execution_roadmap
    ])

    # KPIs
    kpis_md = "\n".join([
        f"- **{kpi.metric_name}**: Target `{kpi.target_kpi}` on `{kpi.channel}`"
        for kpi in strategy.success_metrics
    ])

    # Rationale Alternatives
    alt_critiques = "\n".join([
        f"- **Against `{cid}`**: {critique}"
        for cid, critique in rationale.why_selected_over_alternatives.items()
    ])

    brief_md = f"""# CREATIVEIQ · Master Campaign Creative Brief
**Module 02 · Autonomous Creative Director Handoff (Person 2 ➔ Person 3)**

---

## 1. Executive Summary & Brand Foundation
- **Brand Name**: {campaign_input.brand_name}
- **Industry**: {campaign_input.industry}
- **Core Offering**: {campaign_input.product_name} — {campaign_input.product_description}
- **Target Audience**: {campaign_input.target_audience}
- **Primary Objective**: {campaign_input.campaign_objective}
- **Campaign Duration & Budget**: {campaign_input.campaign_duration} | {campaign_input.campaign_budget or 'Standard Media Tier'}
- **Brand Tone**: {campaign_input.brand_tone}

---

## 2. Winning Campaign Strategy: "{strategy.campaign_name}"
- **Official Campaign Name**: {strategy.campaign_name}
- **Hero Tagline**: **"{strategy.main_tagline}"**
- **The Big Creative Idea**: {strategy.big_creative_idea}
- **Key Marketing Message**: {strategy.key_marketing_message}
- **Emotional Transformation**: {strategy.emotional_positioning}
- **Core Objectives**:
{chr(10).join([f"  - {obj}" for obj in strategy.campaign_objectives])}

---

## 3. Creative Ideation & Autonomous Decision Matrix
The Creative Director engineered 3 distinct strategic concepts and evaluated them across the standardized 4-pillar rubric (25% Creativity, 25% Audience Relevance, 25% Brand Consistency, 25% Objective Alignment):

| Concept & Angle | Creativity | Audience Rel. | Brand Align. | Obj. Align. | Weighted Score | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
{eval_table}

### Autonomous Selection Rationale
- **Winning Concept**: `{winning_concept.concept_id}` — **{winning_concept.concept_name}**
- **Executive Verdict**: {rationale.selection_verdict}
- **Why It Won Over Alternatives**:
{alt_critiques}
- **Brand DNA Alignment**: {rationale.brand_dna_alignment}
- **Competitor White Space Captured**: {rationale.competitor_white_space}
- **Objective Fulfillment**: {rationale.objective_delivery}

---

## 4. Visual Direction Blueprint (For Person 3 Designers & Prompt Engineers)

### Color Palette
| Color Name | Hex Code | Role | Psychological Rationale |
| :--- | :---: | :---: | :--- |
{colors_table}

### Design Style & Aesthetics
- **Aesthetic Direction**: {strategy.visual_direction.design_style}
- **Mood, Lighting & Atmosphere**: {strategy.visual_direction.mood_and_aesthetics}
- **Visual Storytelling Approach**: {strategy.visual_direction.visual_storytelling_approach}

### Typography Direction
- **Headline Font**: **{strategy.visual_direction.typography_direction.headline_font}**
  - *Vibe & Style*: {strategy.visual_direction.typography_direction.headline_style_and_vibe}
- **Body Font**: **{strategy.visual_direction.typography_direction.body_font}**
  - *Vibe & Style*: {strategy.visual_direction.typography_direction.body_style_and_vibe}
- **Hierarchy Guidelines**: {strategy.visual_direction.typography_direction.hierarchy_guidelines}

### GenAI Image Prompts (Midjourney / Flux / DALL-E)
{mj_prompts}

---

## 5. Instagram Platform Execution Engine

### A. Instagram Feed Post ({strategy.platform_strategy.feed_posts.post_type})
- **Visual Layout**: {strategy.platform_strategy.feed_posts.visual_layout}
- **Headline Hook**: **"{strategy.platform_strategy.feed_posts.headline_hook}"**
- **Caption Body**:
> {strategy.platform_strategy.feed_posts.caption_body}
- **Call-To-Action**: `{strategy.platform_strategy.feed_posts.call_to_action}`
- **Carousel Slide Breakdown**:
{carousel_slides_md}
- **Hashtags**: {' '.join(strategy.platform_strategy.feed_posts.hashtags)}

### B. Instagram Stories Sequence
- **Story Arc**: {strategy.platform_strategy.stories.story_arc_theme}
- **Audio & Sound**: {strategy.platform_strategy.stories.sound_and_music_direction}
- **Frame Progression**:
{story_frames_md}
- **Story CTA**: `{strategy.platform_strategy.stories.story_cta}`

### C. Instagram Reels / Video Ad ({strategy.platform_strategy.advertisements_and_reels.video_duration})
- **0–3s Scroll-Stopping Hook**: {strategy.platform_strategy.advertisements_and_reels.hook_0_to_3s}
- **3–10s Problem & Tension**: {strategy.platform_strategy.advertisements_and_reels.problem_tension_3_to_10s}
- **10–20s Solution & Product in Motion**: {strategy.platform_strategy.advertisements_and_reels.solution_product_10_to_20s}
- **20–30s Climax & Conversion CTA**: {strategy.platform_strategy.advertisements_and_reels.climax_cta_20_to_30s}
- **Audio & Voiceover Direction**: {strategy.platform_strategy.advertisements_and_reels.audio_and_voiceover}
- **On-Screen Text Overlays**: {', '.join(strategy.platform_strategy.advertisements_and_reels.on_screen_text_hooks)}

---

## 6. Execution Roadmap & Performance Metrics
### Phased Rollout
{roadmap_md}

### Target Success Metrics (KPIs)
{kpis_md}

- **Projected Market Impact**: {strategy.expected_outcomes}

---
*Generated autonomously by CREATIVEIQ Module 02 (Autonomous Creative Director Agent)*
"""
    return brief_md
