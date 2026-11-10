from typing import Dict, Any
from app.ai.llm_gateway import llm_gateway, LLMGateway
from app.schemas.campaign_schema import (
    CampaignInput,
    CampaignConcept,
    MasterCampaignStrategy
)


class CampaignStrategySynthesizer:
    """
    Strategy & Visual Direction Synthesizer for Person 2.
    Expands the winning concept into a comprehensive Master Campaign Blueprint:
    - Core Strategy (Name, Tagline, Big Idea, Audience, Emotional Positioning, Key Message, Objectives)
    - Visual Direction Blueprint (Hex Color Palette, Design Style, Typography Spec, Mood, Visual Storytelling, GenAI Prompts)
    - Instagram Platform Strategy (Feed Carousel/Post, Story Sequence with Stickers, 30s Reel/Ad Storyboard)
    - Execution Roadmap & KPIs
    """

    def __init__(self, gateway: LLMGateway = llm_gateway):
        self.gateway = gateway

    def synthesize_strategy(
        self,
        campaign_input: CampaignInput,
        winner: CampaignConcept
    ) -> MasterCampaignStrategy:
        """Generate the complete Master Campaign Strategy based on the winning concept."""
        system_prompt = (
            "You are CREATIVEIQ's Master Brand Strategist and Visual Art Director. "
            "Translate winning creative concepts into actionable, impeccably detailed campaign blueprints. "
            "Your visual direction is concrete with exact hex codes. "
            "Your Instagram platform execution is conversion-engineered. "
            "Return ONLY a clean JSON object matching the requested fields."
        )

        prompt = f"""
BRAND BRIEF:
- Brand Name: {campaign_input.brand_name}
- Industry: {campaign_input.industry}
- Product: {campaign_input.product_name} - {campaign_input.product_description}
- Target Audience: {campaign_input.target_audience}
- Campaign Objectives: {campaign_input.campaign_objectives or [campaign_input.campaign_objective]}
- Tone: {campaign_input.brand_tone}

WINNING CONCEPT:
- Concept Name: {winner.concept_name}
- Main Tagline: {winner.main_tagline}
- Big Creative Idea: {winner.big_creative_idea}
- Emotional Positioning: {winner.emotional_positioning}
- Key Message: {winner.key_marketing_message}

DEVELOP THE COMPLETE CAMPAIGN STRATEGY AS A JSON OBJECT WITH THESE EXACT KEYS:
{{
  "campaign_name": "{winner.concept_name}",
  "main_tagline": "{winner.main_tagline}",
  "big_creative_idea": "{winner.big_creative_idea}",
  "target_audience": "Detailed description of audience segments, psychographics, and lifestyle triggers.",
  "emotional_positioning": "Exact emotional shift from problem state to empowered state.",
  "key_marketing_message": "Central marketing proposition.",
  "campaign_objectives": ["Objective 1", "Objective 2", "Objective 3"],
  "visual_direction": {{
    "colour_palette": [
      {{"color_name": "...", "hex_code": "#1A2B3C", "role": "Primary", "psychological_rationale": "..."}},
      {{"color_name": "...", "hex_code": "#D4AF37", "role": "Secondary", "psychological_rationale": "..."}},
      {{"color_name": "...", "hex_code": "#EAEAEA", "role": "Background", "psychological_rationale": "..."}},
      {{"color_name": "...", "hex_code": "#FF5733", "role": "Accent", "psychological_rationale": "..."}}
    ],
    "design_style": "e.g. Modern Minimalist Editorial with Textured Contrast",
    "typography_direction": {{
      "headline_font": "Clash Display Bold",
      "headline_style_and_vibe": "Bold, authoritative, contemporary geometric",
      "body_font": "Inter Regular",
      "body_style_and_vibe": "Clean, highly legible modern sans-serif",
      "hierarchy_guidelines": "High-contrast scale pairing large bold headlines with airy body copy"
    }},
    "mood_and_aesthetics": "Lighting, materials, camera focus, atmosphere, depth",
    "visual_storytelling_approach": "Visual metaphors, compositional framing, recurring visual motifs",
    "midjourney_prompts": [
      "Cinematic editorial commercial photograph of [subject], soft golden-hour natural window lighting, 35mm lens, 8k resolution, minimalist architectural background --ar 4:5",
      "Macro detailed close-up shot of [product] with water droplets, pristine studio softbox illumination, hyper-realistic textures --ar 1:1",
      "Lifestyle portrait of young professional in modern minimalist interior interacting with [product], authentic candid expression --ar 9:16"
    ]
  }},
  "platform_strategy": {{
    "feed_posts": {{
      "post_type": "Carousel",
      "visual_layout": "Clean vertical 4:5 layout with strong focal hierarchy",
      "headline_hook": "...",
      "caption_body": "...",
      "call_to_action": "...",
      "carousel_slide_breakdown": [
        "Slide 1: High-impact hook statement",
        "Slide 2: Agitation of daily friction/status quo",
        "Slide 3: The mindset shift & product introduction",
        "Slide 4: Key benefits and proof points",
        "Slide 5: Final CTA and community invite"
      ],
      "hashtags": ["#BrandTag", "#CampaignTag", "#TopicTag"]
    }},
    "stories": {{
      "story_arc_theme": "Behind the daily ritual: From chaos to clarity",
      "frames": [
        {{"frame_number": 1, "visual_scene": "Relatable problem scene", "overlay_copy": "Be honest...", "interactive_sticker": "Poll: Yes / No"}},
        {{"frame_number": 2, "visual_scene": "Product in natural context", "overlay_copy": "Meet your upgrade", "interactive_sticker": "Emoji Slider"}},
        {{"frame_number": 3, "visual_scene": "User transformation", "overlay_copy": "Ready to switch?", "interactive_sticker": "Quiz Sticker"}},
        {{"frame_number": 4, "visual_scene": "Final packshot with link", "overlay_copy": "Shop the drop", "interactive_sticker": "Link Sticker"}}
      ],
      "sound_and_music_direction": "Chill indie-electronic beat with crisp natural Foley sounds",
      "story_cta": "Tap link sticker to get 15% off during launch week"
    }},
    "advertisements_and_reels": {{
      "video_duration": "15-30s",
      "hook_0_to_3s": "Fast visual pattern-interrupt with unexpected question or statement",
      "problem_tension_3_to_10s": "Quick-cut relatable daily struggle",
      "solution_product_10_to_20s": "Dynamic product interaction demonstrating transformation",
      "climax_cta_20_to_30s": "Bold punchline tagline with on-screen coupon code and shop button",
      "audio_and_voiceover": "Confident, friendly conversational voiceover paired with upbeat bassline",
      "on_screen_text_hooks": ["Stop doing it the hard way", "The 10-second switch", "Try it risk-free"]
    }}
  }},
  "execution_roadmap": [
    {{"phase_name": "Phase 1: Tease & Intrigue", "timeline": "Week 1", "key_activities": ["Cryptic teaser stories", "Influencer seed gifting", "Waitlist opening"]}},
    {{"phase_name": "Phase 2: Official Launch", "timeline": "Weeks 2-3", "key_activities": ["Hero carousel drops", "Paid Instagram Reels blitz", "User-generated challenge"]}},
    {{"phase_name": "Phase 3: Social Proof & Retargeting", "timeline": "Week 4+", "key_activities": ["Customer reviews carousel", "Dynamic retargeting ads", "Limited bundle incentive"]}}
  ],
  "success_metrics": [
    {{"metric_name": "Instagram Engagement Rate", "target_kpi": "> 5.2%", "channel": "Feed Carousels"}},
    {{"metric_name": "Video Completion Rate", "target_kpi": "> 40%", "channel": "Reels & Paid Ads"}},
    {{"metric_name": "Direct Return on Ad Spend (ROAS)", "target_kpi": "3.8x", "channel": "Paid Instagram Ads"}}
  ],
  "expected_outcomes": "High viral talkability, rapid early adoption among target cohort, and sustainable direct conversion."
}}
"""
        response_dict = self.gateway.generate_json(prompt, system_prompt=system_prompt)

        # Handle case where LLM wraps under 'strategy' or 'campaign_strategy'
        if "strategy" in response_dict and isinstance(response_dict["strategy"], dict):
            response_dict = response_dict["strategy"]
        elif "campaign_strategy" in response_dict and isinstance(response_dict["campaign_strategy"], dict):
            response_dict = response_dict["campaign_strategy"]

        # Ensure essential keys
        if "campaign_name" not in response_dict or not response_dict["campaign_name"]:
            response_dict["campaign_name"] = winner.concept_name
        if "main_tagline" not in response_dict or not response_dict["main_tagline"]:
            response_dict["main_tagline"] = winner.main_tagline
        if "big_creative_idea" not in response_dict or not response_dict["big_creative_idea"]:
            response_dict["big_creative_idea"] = winner.big_creative_idea

        return MasterCampaignStrategy.model_validate(response_dict)


campaign_strategy_synthesizer = CampaignStrategySynthesizer()
