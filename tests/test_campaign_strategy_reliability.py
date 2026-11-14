import json
from collections.abc import Sequence

import pytest

from app.schemas.campaign_schema import CampaignConcept, CampaignInput
from app.services.campaign_strategy import (
    CampaignStrategySynthesizer,
    StrategyResponseError,
)


class FakeGateway:
    def __init__(self, responses: Sequence[str]):
        self.responses = list(responses)
        self.prompts: list[str] = []
        self.output_budgets: list[int] = []

    def generate(self, prompt, system_prompt=None, max_tokens=2048):
        self.prompts.append(prompt)
        self.output_budgets.append(max_tokens)
        if not self.responses:
            raise AssertionError("Unexpected extra strategy model call")
        return self.responses.pop(0)


def make_input():
    return CampaignInput(
        brand_name="Northstar",
        industry="Outdoor gear",
        product_name="Trail Pack",
        product_description="A repairable day pack.",
        target_audience="Weekend hikers",
        campaign_objective="Increase launch awareness",
        campaign_objectives=["Increase awareness", "Drive product trials"],
        campaign_duration="30 Days",
        campaign_platforms=["Instagram", "Email"],
    )


def make_concept():
    return CampaignConcept(
        concept_id="CONCEPT_2",
        concept_name="The Repairable Trail",
        main_tagline="Keep going, gear included.",
        big_creative_idea="Show repair as part of the hiking ritual.",
        creative_angle="Community & Lifestyle Ritual",
        target_audience_focus="Weekend hikers",
        emotional_positioning="From replaceable to dependable",
        key_marketing_message="A pack designed to stay on the trail.",
        unique_angle_vs_competitors="Visible repairability and long-term use.",
        content_hooks=["Hook one", "Hook two", "Hook three"],
    )


def valid_strategy():
    return {
        "campaign_name": "The Repairable Trail",
        "selected_concept_id": "CONCEPT_2",
        "main_tagline": "Keep going, gear included.",
        "big_creative_idea": "Show repair as part of the hiking ritual.",
        "target_audience": "Weekend hikers",
        "emotional_positioning": "From replaceable to dependable",
        "key_marketing_message": "A pack designed to stay on the trail.",
        "campaign_objectives": ["Increase launch awareness", "Drive product trials"],
        "visual_direction": {
            "colour_palette": [
                {"color_name": "Forest", "hex_code": "#176B45", "role": "Primary"},
                {"color_name": "Sky", "hex_code": "#A9D6E5", "role": "Secondary"},
                {"color_name": "Stone", "hex_code": "#D8D2C4", "role": "Background"},
                {"color_name": "Berry", "hex_code": "#B23A48", "role": "Accent"},
            ],
            "design_style": "Documentary outdoor editorial",
            "midjourney_prompts": ["Trail image one", "Trail image two", "Trail image three"],
        },
        "platform_strategy": {
            "feed_posts": {
                "carousel_slide_breakdown": ["Slide one", "Slide two", "Slide three"]
            },
            "stories": {
                "frames": [
                    {"frame_number": 1, "visual_scene": "Trailhead", "overlay_copy": "Pack for the long run", "interactive_sticker": "Poll"},
                    {"frame_number": 2, "visual_scene": "Strap repair", "overlay_copy": "Fix it, keep going", "interactive_sticker": "Question box"},
                    {"frame_number": 3, "visual_scene": "Summit", "overlay_copy": "Where will yours go?", "interactive_sticker": "Emoji slider"},
                ]
            },
        },
        "execution_roadmap": [
            {"phase_name": "Launch", "timeline": "Days 1-30", "key_activities": ["Publish the campaign"]}
        ],
        "success_metrics": [
            {"metric_name": "Awareness", "target_kpi": "Proposed target: compare reach with baseline", "channel": "Instagram"}
        ],
        "expected_outcomes": "Proposed awareness lift, measured against baseline.",
    }


def synthesize(response: str):
    gateway = FakeGateway([response])
    result = CampaignStrategySynthesizer(gateway).synthesize_strategy(
        make_input(), make_concept()
    )
    return result, gateway


def test_valid_json_strategy_is_validated():
    result, gateway = synthesize(json.dumps(valid_strategy()))

    assert result.campaign_name == "The Repairable Trail"
    assert result.selected_concept_id == "CONCEPT_2"
    assert len(result.platform_strategy.stories.frames) == 3
    assert len(gateway.prompts) == 1
    assert gateway.output_budgets == [4096]


def test_fenced_prefaced_nested_strategy_json_is_supported():
    response = {
        "campaign_strategy": valid_strategy(),
        "metadata": {"provider": "test"},
    }
    gateway = FakeGateway([
        "Strategy output follows:\n```json\n"
        + json.dumps(response)
        + "\n```"
    ])

    result = CampaignStrategySynthesizer(gateway).synthesize_strategy(
        make_input(), make_concept()
    )

    assert result.campaign_name == "The Repairable Trail"
    assert result.selected_concept_id == "CONCEPT_2"


def test_malformed_json_retries_with_parse_error_and_succeeds():
    gateway = FakeGateway([
        '{"campaign_name": "broken", "platform_strategy": {',
        json.dumps(valid_strategy()),
    ])

    result = CampaignStrategySynthesizer(gateway).synthesize_strategy(
        make_input(), make_concept()
    )

    assert result.campaign_name == "The Repairable Trail"
    assert len(gateway.prompts) == 2
    assert "Malformed strategy JSON" in gateway.prompts[1]


def test_malformed_outer_json_never_salvages_nested_object():
    raw_response = '{"campaign_strategy":{"campaign_name":"nested"}, "broken": '

    with pytest.raises(StrategyResponseError, match="Malformed strategy JSON"):
        CampaignStrategySynthesizer._parse_json_object(raw_response)


def test_missing_required_field_retries_then_fails():
    incomplete = valid_strategy()
    del incomplete["campaign_name"]
    gateway = FakeGateway([json.dumps(incomplete), json.dumps(incomplete)])

    with pytest.raises(StrategyResponseError, match="2 attempts") as exc_info:
        CampaignStrategySynthesizer(gateway).synthesize_strategy(
            make_input(), make_concept()
        )

    assert "campaign_name" in str(exc_info.value)
    assert "campaign_name" in gateway.prompts[1]
    assert len(gateway.prompts) == 2


def test_missing_story_interactive_elements_retries_then_fails():
    incomplete = valid_strategy()
    incomplete["platform_strategy"]["stories"]["frames"][0].pop(
        "interactive_sticker"
    )
    gateway = FakeGateway([json.dumps(incomplete), json.dumps(incomplete)])

    with pytest.raises(StrategyResponseError, match="interactive_sticker"):
        CampaignStrategySynthesizer(gateway).synthesize_strategy(
            make_input(), make_concept()
        )

    assert len(gateway.prompts) == 2
    assert "interactive_sticker" in gateway.prompts[1]


def test_missing_story_frames_retries_and_accepts_corrected_frames():
    incomplete = valid_strategy()
    incomplete["platform_strategy"]["stories"]["frames"] = [
        {"frame_number": 1, "visual_scene": "Trailhead", "overlay_copy": "Start"}
    ]
    gateway = FakeGateway([json.dumps(incomplete), json.dumps(valid_strategy())])

    result = CampaignStrategySynthesizer(gateway).synthesize_strategy(
        make_input(), make_concept()
    )

    assert len(result.platform_strategy.stories.frames) == 3
    assert "at least three frames" in gateway.prompts[1]


def test_all_retries_fail_gracefully_with_actual_last_error():
    gateway = FakeGateway(["not json", "still not json"])

    with pytest.raises(StrategyResponseError, match="2 attempts") as exc_info:
        CampaignStrategySynthesizer(gateway).synthesize_strategy(
            make_input(), make_concept()
        )

    assert "did not contain a JSON object" in str(exc_info.value)
    assert len(gateway.prompts) == 2
