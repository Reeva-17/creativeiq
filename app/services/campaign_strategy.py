
import json
import re
from typing import Any, Dict

from app.ai.llm_gateway import llm_gateway
from app.schemas.campaign_schema import (
    CampaignInput,
    CampaignConcept,
    MasterCampaignStrategy,
)


class StrategyResponseError(ValueError):
    """The strategy model response could not satisfy the campaign contract."""


class CampaignStrategySynthesizer:
    """
    Converts the selected creative concept into a structured campaign strategy.
    Uses the actual campaign brief instead of relying on generic assumptions.
    """

    def __init__(self, gateway=None):
        self.gateway = gateway or llm_gateway

    MAX_ATTEMPTS = 2
    # The schema is detailed, but 4k is ample and avoids requesting more than
    # the free-tier provider's available burst budget in one strategy call.
    MAX_OUTPUT_TOKENS = 4096

    @staticmethod
    def _parse_json_object(raw_response: str) -> Dict[str, Any]:
        if not isinstance(raw_response, str) or not raw_response.strip():
            raise StrategyResponseError("Model returned an empty strategy response.")

        cleaned = re.sub(
            r"^\s*```(?:json)?\s*|\s*```\s*$",
            "",
            raw_response.strip(),
            flags=re.IGNORECASE,
        )
        candidate = re.search(r"\{\s*\"", cleaned)
        if candidate is None:
            raise StrategyResponseError(
                "Strategy response did not contain a JSON object; "
                f"response excerpt={cleaned[:200]!r}"
            )

        decoder = json.JSONDecoder()
        try:
            value, _ = decoder.raw_decode(cleaned[candidate.start():])
        except json.JSONDecodeError as exc:
            excerpt = cleaned[max(0, candidate.start() + exc.pos - 100):
                              candidate.start() + exc.pos + 160]
            raise StrategyResponseError(
                "Malformed strategy JSON: "
                f"{exc.msg} at line {exc.lineno}, column {exc.colno}; "
                f"response excerpt={excerpt!r}"
            ) from exc

        if not isinstance(value, dict):
            raise StrategyResponseError("Strategy JSON must be an object.")
        return value

    @staticmethod
    def _unwrap_response(response: Dict[str, Any]) -> Dict[str, Any]:
        for key in ("strategy", "campaign_strategy"):
            nested = response.get(key)
            if nested is not None:
                if not isinstance(nested, dict):
                    raise StrategyResponseError(
                        f"Response field {key!r} must be a JSON object."
                    )
                return nested
        return response

    @staticmethod
    def _validate_story_frames(strategy_data: Dict[str, Any]) -> None:
        platform = strategy_data.get("platform_strategy")
        stories = platform.get("stories") if isinstance(platform, dict) else None
        frames = stories.get("frames") if isinstance(stories, dict) else None
        if not isinstance(frames, list) or len(frames) < 3:
            raise StrategyResponseError(
                "platform_strategy.stories.frames must contain at least three frames."
            )
        required_fields = (
            "frame_number",
            "visual_scene",
            "overlay_copy",
            "interactive_sticker",
        )
        for index, frame in enumerate(frames, start=1):
            if not isinstance(frame, dict):
                raise StrategyResponseError(
                    f"Story frame {index} must be an object."
                )
            missing = [
                field
                for field in required_fields
                if frame.get(field) is None
                or (isinstance(frame.get(field), str) and not frame[field].strip())
            ]
            if missing:
                raise StrategyResponseError(
                    f"Story frame {index} is missing required fields: "
                    f"{', '.join(missing)}."
                )

    @classmethod
    def _validate_strategy_data(
      cls,
      strategy_data: Dict[str, Any],
      winning_concept: CampaignConcept,
    ) -> MasterCampaignStrategy:
        # This identifier comes from the locally selected concept, not the model.
        strategy_data["selected_concept_id"] = winning_concept.concept_id
        cls._validate_story_frames(strategy_data)
        try:
            strategy = MasterCampaignStrategy.model_validate(strategy_data)
        except Exception as exc:
            raise StrategyResponseError(
                f"Strategy does not match MasterCampaignStrategy: {exc}"
            ) from exc

        if len(strategy.visual_direction.midjourney_prompts) < 3:
            raise StrategyResponseError(
                "visual_direction.midjourney_prompts must contain at least three prompts."
            )
        if len(strategy.platform_strategy.feed_posts.carousel_slide_breakdown) < 3:
            raise StrategyResponseError(
                "platform_strategy.feed_posts.carousel_slide_breakdown "
                "must contain at least three slides."
            )
        if not strategy.execution_roadmap:
            raise StrategyResponseError("execution_roadmap must not be empty.")
        if not strategy.success_metrics:
            raise StrategyResponseError("success_metrics must not be empty.")
        return strategy

    def synthesize_strategy(
        self,
        campaign_input: CampaignInput,
        winning_concept: CampaignConcept,
    ) -> MasterCampaignStrategy:

        system_prompt = """
You are CREATIVEIQ's Senior Campaign Strategy Director.

Create a practical, brand-specific campaign strategy using the supplied
campaign information and the selected creative concept.

Important instructions:
- Use the actual brand identity, target audience and campaign objectives.
- Respect the campaign budget and duration.
- Use the requested platforms. Do not assume every campaign is Instagram-only.
- Do not invent guaranteed results or claim that estimated KPIs are certain.
- Make KPI targets realistic and label them as proposed targets.
- Make the execution roadmap fit the supplied campaign duration.
- Keep the visual direction consistent with the brand and concept.
- Do not change the selected creative concept.
- Return at least four and no more than five exact HEX palette colors.
- Return at least three image-generation prompts and three carousel slides.
- Return at least three story frame objects. Every frame must include
    frame_number, visual_scene, overlay_copy, and a non-empty interactive_sticker.
- Return a non-empty execution_roadmap and success_metrics array.
- Include every required field; do not omit fields or replace objects with strings.
- Return ONLY valid JSON.

Return this structure:

{
  "campaign_name": "...",
    "selected_concept_id": "<the supplied winning concept ID>",
  "main_tagline": "...",
  "big_creative_idea": "...",
  "target_audience": "...",
  "emotional_positioning": "...",
  "key_marketing_message": "...",
  "campaign_objectives": ["..."],
  "visual_direction": {
    "colour_palette": [
      {
        "color_name": "...",
        "hex_code": "#000000",
        "role": "...",
        "psychological_rationale": "..."
      }
    ],
    "design_style": "...",
    "typography_direction": {
      "headline_font": "...",
      "headline_style_and_vibe": "...",
      "body_font": "...",
      "body_style_and_vibe": "...",
      "hierarchy_guidelines": "..."
    },
    "mood_and_aesthetics": "...",
    "visual_storytelling_approach": "...",
    "midjourney_prompts": ["Detailed prompt 1", "Detailed prompt 2", "Detailed prompt 3"]
  },
  "platform_strategy": {
    "feed_posts": {
      "post_type": "Carousel",
      "visual_layout": "...",
      "headline_hook": "...",
      "caption_body": "...",
      "call_to_action": "...",
      "carousel_slide_breakdown": ["Slide 1...", "Slide 2...", "Slide 3..."],
      "hashtags": ["..."]
    },
    "stories": {
      "story_arc_theme": "...",
      "frames": [
        {
          "frame_number": 1,
          "visual_scene": "...",
          "overlay_copy": "...",
          "interactive_sticker": "..."
        },
        {"frame_number": 2, "visual_scene": "...", "overlay_copy": "...", "interactive_sticker": "..."},
        {"frame_number": 3, "visual_scene": "...", "overlay_copy": "...", "interactive_sticker": "..."}
      ],
      "sound_and_music_direction": "...",
      "story_cta": "..."
    },
    "advertisements_and_reels": {
      "video_duration": "15-30s",
      "hook_0_to_3s": "...",
      "problem_tension_3_to_10s": "...",
      "solution_product_10_to_20s": "...",
      "climax_cta_20_to_30s": "...",
      "audio_and_voiceover": "...",
      "on_screen_text_hooks": ["..."]
    }
  },
  "execution_roadmap": [
    {
      "phase_name": "...",
      "timeline": "...",
      "key_activities": ["..."]
    }
  ],
  "success_metrics": [
    {
      "metric_name": "...",
      "target_kpi": "Proposed target: ...",
      "channel": "..."
    }
  ],
  "expected_outcomes": "..."
}

The platform_strategy object follows the project's current Instagram schema.
If Instagram is not among the requested platforms, keep its content relevant
to the selected concept but do not claim it is the main campaign channel.
"""

        prompt = f"""
CAMPAIGN INPUT

Brand Name:
{campaign_input.brand_name}

Industry:
{campaign_input.industry}

Product / Service:
{campaign_input.product_name}

Product Description:
{campaign_input.product_description}

Target Audience:
{campaign_input.target_audience}

Primary Campaign Objective:
{campaign_input.campaign_objective}

Additional Campaign Objectives:
{campaign_input.campaign_objectives}

Brand DNA:
{campaign_input.brand_dna}

Brand Tone:
{campaign_input.brand_tone}

Competitors:
{campaign_input.competitors}

Market Gaps:
{campaign_input.market_gaps}

Requested Platforms:
{campaign_input.campaign_platforms}

Campaign Budget:
{campaign_input.campaign_budget}

Campaign Duration:
{campaign_input.campaign_duration}

Key Messages:
{campaign_input.key_messages}

Additional Requirements:
{campaign_input.additional_requirements}


SELECTED CREATIVE CONCEPT

Concept ID:
{winning_concept.concept_id}

Concept Name:
{winning_concept.concept_name}

Tagline:
{winning_concept.main_tagline}

Big Creative Idea:
{winning_concept.big_creative_idea}

Creative Angle:
{winning_concept.creative_angle}

Target Audience Focus:
{winning_concept.target_audience_focus}

Emotional Positioning:
{winning_concept.emotional_positioning}

Key Marketing Message:
{winning_concept.key_marketing_message}

Unique Angle:
{winning_concept.unique_angle_vs_competitors}

Content Hooks:
{winning_concept.content_hooks}

Visual Teaser:
{winning_concept.visual_hook_teaser}


TASK

Develop a complete campaign strategy based on this exact input.

Make the roadmap fit the campaign duration.
Make the success metrics relevant to the objectives and requested platforms.
Do not invent budget figures or guaranteed performance results.
Return the JSON structure specified in the system instructions.
"""

        last_error: Exception | None = None
        retry_feedback = ""
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            attempt_prompt = prompt
            if retry_feedback:
                attempt_prompt += (
                    "\n\nRETRY REQUIREMENTS\n"
                    "Your previous response failed parsing or validation. "
                    "Correct these exact errors and return the complete strategy.\n"
                    f"{retry_feedback}\n"
                    "Do not omit, shorten, or replace required nested sections."
                )
            try:
                raw_response = self.gateway.generate(
                    attempt_prompt,
                    system_prompt=system_prompt,
                        max_tokens=self.MAX_OUTPUT_TOKENS,
                )
                response = self._parse_json_object(raw_response)
                strategy_data = self._unwrap_response(response)
                strategy = self._validate_strategy_data(
                    strategy_data,
                    winning_concept,
                )
                break
            except Exception as exc:
                last_error = exc
                retry_feedback = str(exc)[:1200]
                if attempt == self.MAX_ATTEMPTS:
                    raise StrategyResponseError(
                        "Campaign strategy generation failed after "
                        f"{self.MAX_ATTEMPTS} attempts. Last error: {exc}"
                    ) from exc
        else:
            raise StrategyResponseError(
                f"Campaign strategy generation failed: {last_error}"
            )

        print(
            f"[Strategy] Created strategy: {strategy.campaign_name}"
        )

        print(
            f"[Strategy] Requested platforms: "
            f"{campaign_input.campaign_platforms}"
        )

        return strategy


# Shared strategy synthesizer instance used by LangGraph.
campaign_strategy_synthesizer = CampaignStrategySynthesizer()
