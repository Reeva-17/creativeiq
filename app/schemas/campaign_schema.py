from typing import Any, List, Optional, Literal, Dict, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator


# =====================================================================
# 1. INPUT SCHEMAS (Person 1 Handoff / Standalone Brief)
# =====================================================================

class CampaignInput(BaseModel):
    """
    Standardized Campaign Input consumed by Person 2.
    Can be loaded directly from Person 1's BrandIntelligenceReport or standalone.
    """
    model_config = ConfigDict(extra="ignore")

    brand_name: str = Field(..., min_length=1, description="Name of the brand")
    industry: str = Field(default="Consumer Brands", description="Industry or sector")
    product_name: str = Field(..., min_length=1, description="Primary product or service focus")
    product_description: str = Field(..., description="Description of the offering and core features")

    target_audience: str = Field(..., description="Target demographic and psychographic profile")
    campaign_objective: str = Field(..., description="Primary business and marketing goal")
    campaign_objectives: List[str] = Field(
        default_factory=list,
        description="List of specific measurable campaign goals"
    )

    brand_dna: Dict[str, Any] = Field(
        default_factory=dict,
        description="Brand identity, values, personality, and tone received from Person 1"
    )
    competitors: List[str] = Field(
        default_factory=list,
        description="Known competitors and their positioning"
    )
    market_gaps: List[str] = Field(
        default_factory=list,
        description="Unmet market needs and competitor white spaces identified by Person 1"
    )

    campaign_platforms: List[str] = Field(
        default_factory=lambda: ["Instagram Feed", "Instagram Stories", "Instagram Reels / Video Ads"],
        description="Target distribution channels"
    )
    campaign_budget: Optional[str] = Field(default=None, description="Allocated media budget")
    campaign_duration: Optional[str] = Field(default="30 Days", description="Campaign run duration")
    brand_tone: Optional[str] = Field(default=None, description="Tone of voice and stylistic guidelines")
    key_messages: List[str] = Field(default_factory=list, description="Must-include messaging pillars")
    additional_requirements: Optional[str] = Field(default=None, description="Special instructions")

    @classmethod
    def from_person_1_report(
        cls,
        report: Dict[str, Any],
        product_name: Optional[str] = None,
        product_description: Optional[str] = None,
        campaign_objective: Optional[str] = None,
        budget: Optional[str] = None,
        duration: Optional[str] = "30 Days"
    ) -> "CampaignInput":
        """Factory method to convert Person 1's BrandIntelligenceReport into CampaignInput."""
        brand_name = report.get("brand_name", "Brand")
        industry = report.get("industry", "Consumer Brand")

        # Extract brand DNA statements
        dna_raw = report.get("brand_dna", {})
        values = [v.get("statement", "") for v in dna_raw.get("values", []) if isinstance(v, dict)]
        personality = [p.get("statement", "") for p in dna_raw.get("personality", []) if isinstance(p, dict)]
        tones = [t.get("statement", "") for t in dna_raw.get("tone_of_voice", []) if isinstance(t, dict)]

        # Extract audience
        audience_info = dna_raw.get("target_audience", {})
        pain_points = [p.get("statement", "") for p in audience_info.get("pain_points", []) if isinstance(p, dict)]
        demographics = [d.get("statement", "") for d in audience_info.get("demographics", []) if isinstance(d, dict)]
        target_audience_str = " | ".join(demographics + pain_points) or "Modern conscious consumers"

        # Extract competitors
        comp_analysis = report.get("competitor_analysis", {})
        direct_comps = [c.get("name") for c in comp_analysis.get("direct_competitors", []) if isinstance(c, dict)]
        gaps = [g.get("statement", "") for g in comp_analysis.get("market_gaps", []) if isinstance(g, dict)]

        # Recommendations
        strat_recs = [r.get("statement", "") for r in report.get("strategic_recommendations", []) if isinstance(r, dict)]

        return cls(
            brand_name=brand_name,
            industry=industry,
            product_name=product_name or f"{brand_name} Signature Line",
            product_description=product_description or f"High-performance offering by {brand_name}.",
            target_audience=target_audience_str,
            campaign_objective=campaign_objective or (strat_recs[0] if strat_recs else "Drive brand awareness and customer acquisition"),
            campaign_objectives=strat_recs[:3] if strat_recs else ["Increase Brand Awareness", "Drive Engagement", "Acquire High-LTV Customers"],
            brand_dna={
                "values": values,
                "personality": personality,
                "tone": tones,
                "raw": dna_raw
            },
            competitors=direct_comps,
            market_gaps=gaps,
            campaign_budget=budget,
            campaign_duration=duration,
            brand_tone=", ".join(tones) if tones else "Authentic, Modern, Inspiring"
        )


# =====================================================================
# 2. CAMPAIGN CONCEPTS (3 Distinct Options)
# =====================================================================

class CampaignConcept(BaseModel):
    """A distinct creative campaign concept developed by the Creative Director."""
    model_config = ConfigDict(extra="ignore")

    concept_id: str = Field(..., description="Unique ID e.g. CONCEPT_1, CONCEPT_2, CONCEPT_3")
    concept_name: str = Field(..., description="Catchy, evocative internal title for the concept")
    main_tagline: str = Field(..., description="Primary consumer-facing campaign tagline")
    big_creative_idea: str = Field(..., description="The core narrative metaphor or creative thesis")
    creative_angle: str = Field(..., description="Strategic archetype (e.g. Emotional, Bold/Disruptive, Cultural/Community)")
    target_audience_focus: str = Field(..., description="How this concept appeals to audience psychographics")
    emotional_positioning: str = Field(..., description="The feeling the campaign evokes in the consumer")
    key_marketing_message: str = Field(..., description="The central takeaway message")
    unique_angle_vs_competitors: str = Field(..., description="How this concept carves a unique position away from competitors")
    content_hooks: List[str] = Field(default_factory=list, description="3 scroll-stopping content hooks for social media")
    visual_hook_teaser: str = Field(default="Striking, high-contrast visual composition.", description="Visual teaser")

    @property
    def campaign_tagline(self) -> str:
        return self.main_tagline


    @field_validator("content_hooks", mode="before")
    @classmethod
    def normalize_hooks(cls, v):
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(item) if not isinstance(item, dict) else " - ".join(f"{k}: {val}" for k, val in item.items()) for item in v]
        return []


# =====================================================================
# 3. AUTONOMOUS EVALUATION & DECISION MAKING
# =====================================================================

class EvaluationCriteriaScores(BaseModel):
    creativity: float = Field(..., ge=0, le=10)
    audience_relevance: float = Field(..., ge=0, le=10)
    brand_consistency: float = Field(..., ge=0, le=10)
    campaign_objectives_alignment: float = Field(..., ge=0, le=10)
    feasibility: float = Field(default=8.5, ge=0, le=10)
    impact_potential: float = Field(default=8.5, ge=0, le=10)


class ConceptEvaluation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    concept_id: str
    scores: EvaluationCriteriaScores
    overall_score: float = Field(..., ge=0, le=10)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    evaluation_summary: str
    selection_status: Literal["selected", "rejected"]

    @field_validator("strengths", "weaknesses", "improvement_suggestions", mode="before")
    @classmethod
    def normalize_str_lists(cls, v):
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(i) if not isinstance(i, dict) else list(i.values())[0] for i in v]
        return []


class CampaignRationale(BaseModel):
    model_config = ConfigDict(extra="ignore")

    selected_concept_id: str
    selection_verdict: str
    why_selected_over_alternatives: Dict[str, str] = Field(default_factory=dict)
    brand_dna_alignment: str
    competitor_white_space: str
    objective_delivery: str

    @field_validator("why_selected_over_alternatives", mode="before")
    @classmethod
    def normalize_alternatives(cls, v):
        if isinstance(v, list):
            # If list of dicts [{'concept': 'C1', 'reason': '...'}]
            result = {}
            for idx, item in enumerate(v, start=1):
                if isinstance(item, dict):
                    k = item.get("concept_id") or item.get("concept") or f"CONCEPT_{idx}"
                    val = item.get("reason") or item.get("critique") or str(item)
                    result[k] = val
                else:
                    result[f"CONCEPT_{idx}"] = str(item)
            return result
        return v if isinstance(v, dict) else {}


# =====================================================================
# 4. VISUAL DIRECTION BLUEPRINT
# =====================================================================

class ColorSwatch(BaseModel):
    color_name: str
    hex_code: str
    role: str = "Accent"
    psychological_rationale: str = "Evokes premium visual harmony and emotional resonance."

    @field_validator("hex_code", mode="before")
    @classmethod
    def clean_hex(cls, v):
        v_str = str(v).strip()
        if not v_str.startswith("#"):
            v_str = "#" + v_str
        return v_str[:7]


class TypographySpec(BaseModel):
    headline_font: str = "Clash Display Bold"
    headline_style_and_vibe: str = "Authoritative, modern geometric styling with tight letter-spacing."
    body_font: str = "Inter"
    body_style_and_vibe: str = "Clean, highly readable sans-serif with open apertures."
    hierarchy_guidelines: str = "Hero headlines at 48pt+, subheadings at 24pt, body copy at 14-16pt with 1.5 line height."


class VisualDirection(BaseModel):
    model_config = ConfigDict(extra="ignore")

    colour_palette: List[ColorSwatch] = Field(
        default_factory=lambda: [
            ColorSwatch(color_name="Deep Obsidian", hex_code="#121212", role="Primary", psychological_rationale="Grounds the brand with premium authority"),
            ColorSwatch(color_name="Nordic Cloud", hex_code="#F4F6F8", role="Background", psychological_rationale="Provides spacious breathable negative space"),
            ColorSwatch(color_name="Vibrant Sage", hex_code="#4A7C59", role="Accent", psychological_rationale="Evokes organic vitality and fresh energy"),
            ColorSwatch(color_name="Warm Terracotta", hex_code="#E07A5F", role="Secondary", psychological_rationale="Brings human warmth and emotional connection")
        ]
    )
    design_style: str = "Editorial Minimalist with Textured Depth"
    typography_direction: TypographySpec = Field(default_factory=TypographySpec)
    mood_and_aesthetics: str = "Soft diffused cinematic daylight, natural tactile textures, dynamic shadows."
    visual_storytelling_approach: str = "Subject-first framing capturing candid micro-moments and authentic emotional transformations."
    midjourney_prompts: List[str] = Field(default_factory=list)

    @field_validator("typography_direction", mode="before")
    @classmethod
    def normalize_typography(cls, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            return TypographySpec(headline_font=v, body_font="Inter")
        return TypographySpec()


# =====================================================================
# 5. PLATFORM STRATEGY (Instagram Engine)
# =====================================================================

class InstagramFeedPost(BaseModel):
    post_type: Literal["Carousel", "Single Image"] = "Carousel"
    visual_layout: str = "Clean 4:5 vertical grid with focal subject centered and generous negative space."
    headline_hook: str = "Stop settling for ordinary."
    caption_body: str = "Here is what happens when you prioritize real transformation over temporary fixes."
    call_to_action: str = "Tap the link in bio to explore the collection."
    carousel_slide_breakdown: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)

    @field_validator("carousel_slide_breakdown", "hashtags", mode="before")
    @classmethod
    def normalize_list(cls, v):
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(i) if not isinstance(i, dict) else list(i.values())[0] for i in v]
        return []


class StoryFrame(BaseModel):
    frame_number: int = 1
    visual_scene: str = "Close-up hero visual"
    overlay_copy: str = "Did you know?"
    interactive_sticker: str = "Poll: Yes / No"


class InstagramStorySequence(BaseModel):
    story_arc_theme: str = "Behind the transformation: A 3-part daily ritual."
    frames: List[StoryFrame] = Field(default_factory=list)
    sound_and_music_direction: str = "Uplifting acoustic lo-fi beat with ambient outdoor Foley."
    story_cta: str = "Swipe up / Tap link to claim your launch bonus."

    @field_validator("frames", mode="before")
    @classmethod
    def normalize_frames(cls, v):
        if not isinstance(v, list):
            return []
        res = []
        for idx, item in enumerate(v, start=1):
            if isinstance(item, dict):
                res.append(StoryFrame(
                    frame_number=item.get("frame_number", idx),
                    visual_scene=str(item.get("visual_scene", "Engaging visual frame")),
                    overlay_copy=str(item.get("overlay_copy", item.get("copy", ""))),
                    interactive_sticker=str(item.get("interactive_sticker", item.get("sticker", "Poll")))
                ))
            elif isinstance(item, str):
                res.append(StoryFrame(frame_number=idx, visual_scene=item, overlay_copy="", interactive_sticker="Poll"))
        return res


class InstagramAdReel(BaseModel):
    video_duration: str = "15-30s"
    hook_0_to_3s: str = "Dynamic quick-cut visual hook with unexpected question."
    problem_tension_3_to_10s: str = "Fast relatable montage illustrating daily frustration."
    solution_product_10_to_20s: str = "Hero product revealed with smooth dynamic macro movement."
    climax_cta_20_to_30s: str = "Final confident product shot with animated CTA sticker."
    audio_and_voiceover: str = "Upbeat rhythmic synth groove with calm, conversational voiceover."
    on_screen_text_hooks: List[str] = Field(default_factory=list)

    @field_validator("on_screen_text_hooks", mode="before")
    @classmethod
    def normalize_hooks(cls, v):
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(i) for i in v]
        return []


class InstagramPlatformStrategy(BaseModel):
    feed_posts: InstagramFeedPost = Field(default_factory=InstagramFeedPost)
    stories: InstagramStorySequence = Field(default_factory=InstagramStorySequence)
    advertisements_and_reels: InstagramAdReel = Field(default_factory=InstagramAdReel)

    @field_validator("feed_posts", "stories", "advertisements_and_reels", mode="before")
    @classmethod
    def normalize_subsections(cls, v):
        if isinstance(v, dict):
            return v
        return {}


# =====================================================================
# 6. MASTER CAMPAIGN STRATEGY
# =====================================================================

class ExecutionPhase(BaseModel):
    phase_name: str = "Phase 1: Launch"
    timeline: str = "Days 1-10"
    key_activities: List[str] = Field(default_factory=list)


class KPIItem(BaseModel):
    metric_name: str = "Engagement Rate"
    target_kpi: str = "> 4.5%"
    channel: str = "Instagram"


class MasterCampaignStrategy(BaseModel):
    """Complete strategic blueprint for the winning campaign."""
    model_config = ConfigDict(extra="ignore")

    campaign_name: str
    selected_concept_id: str | None = None
    main_tagline: str
    big_creative_idea: str
    target_audience: str
    emotional_positioning: str
    key_marketing_message: str
    campaign_objectives: List[str] = Field(default_factory=list)
    visual_direction: VisualDirection = Field(default_factory=VisualDirection)
    platform_strategy: InstagramPlatformStrategy = Field(default_factory=InstagramPlatformStrategy)
    execution_roadmap: List[ExecutionPhase] = Field(default_factory=list)
    success_metrics: List[KPIItem] = Field(default_factory=list)
    expected_outcomes: str = "Significant brand awareness lift, elevated CTR, and sustainable organic advocacy."

    @field_validator("target_audience", mode="before")
    @classmethod
    def coerce_target_audience(cls, v):
        if isinstance(v, dict):
            return " | ".join(f"{k}: {val}" for k, val in v.items())
        return str(v)

    @field_validator("expected_outcomes", mode="before")
    @classmethod
    def coerce_expected_outcomes(cls, v):
        if isinstance(v, (dict, list)):
            return str(v)
        return str(v) if v else "Accelerated market penetration and high audience conversion."

    @field_validator("campaign_objectives", mode="before")
    @classmethod
    def coerce_objectives(cls, v):
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(i) if not isinstance(i, dict) else list(i.values())[0] for i in v]
        return []

    @field_validator("execution_roadmap", mode="before")
    @classmethod
    def coerce_roadmap(cls, v):
        if not isinstance(v, list):
            return []
        res = []
        for idx, item in enumerate(v, start=1):
            if isinstance(item, dict):
                phase_name = item.get("phase_name") or item.get("phase") or f"Phase {idx}"
                timeline = item.get("timeline") or item.get("timing") or f"Week {idx}"
                activities = item.get("key_activities") or item.get("activities") or []
                if isinstance(activities, str):
                    activities = [activities]
                res.append(ExecutionPhase(phase_name=str(phase_name), timeline=str(timeline), key_activities=[str(a) for a in activities]))
            elif isinstance(item, str):
                res.append(ExecutionPhase(phase_name=f"Phase {idx}", timeline=f"Stage {idx}", key_activities=[item]))
        return res

    @field_validator("success_metrics", mode="before")
    @classmethod
    def coerce_metrics(cls, v):
        if not isinstance(v, list):
            return []
        res = []
        for item in v:
            if isinstance(item, dict):
                metric = item.get("metric_name") or item.get("metric") or "Engagement"
                target = item.get("target_kpi") or item.get("target") or "Growth"
                channel = item.get("channel") or "Instagram"
                res.append(KPIItem(metric_name=str(metric), target_kpi=str(target), channel=str(channel)))
            elif isinstance(item, str):
                res.append(KPIItem(metric_name=item, target_kpi="Positive ROI", channel="All Channels"))
        return res


# =====================================================================
# 7. FINAL HANDOFF BLUEPRINT FOR PERSON 3
# =====================================================================

class CreativeDirectorHandoff(BaseModel):
    model_config = ConfigDict(extra="ignore")

    module: str = Field(default="Module 02 · Campaign Strategy & Decision Making")
    schema_version: str = Field(default="2.0.0")
    brand_name: str
    industry: str
    campaign_name: str
    selected_concept_id: str

    generated_concepts: List[CampaignConcept]
    concept_evaluations: List[ConceptEvaluation]
    campaign_rationale: CampaignRationale
    campaign_strategy: MasterCampaignStrategy
    creative_brief_markdown: str

    @property
    def campaign(self):
        handoff = self
        class _LegacyCampaignView:
            def __init__(self, h):
                self.concepts = h.generated_concepts
                self.evaluations = h.concept_evaluations
                self.selected_concept_id = h.selected_concept_id
                self.selection_reason = h.campaign_rationale.selection_verdict
        return _LegacyCampaignView(handoff)

    @property
    def strategy(self):
        return self.campaign_strategy
