import sys
import os
import json
import pytest

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Adds the root 'creativeiq' directory to Python's module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.creative_director import AutonomousCreativeDirector

pytestmark = pytest.mark.integration


def test_creative_director():
    print("[INIT] Initializing Autonomous Creative Director (Person 2)...")
    director = AutonomousCreativeDirector()

    print("\n[TEST] Running with the configured live LLM provider...")
    # Passing None triggers fallback logic since Person 1 isn't ready yet
    raw_response = director.generate_campaign_blueprint(person_1_output=None)

    print("\n[RAW RESPONSE] Received structured response:")
    print("-" * 50)
    print(raw_response[:500] + "\n...[truncated for display]...")
    print("-" * 50)

    # Validate that it parses cleanly into valid JSON
    try:
        parsed_json = json.loads(raw_response)
        print("\n[SUCCESS] Response successfully parsed as valid JSON!")
        print(f"Selected Concept ID: {parsed_json.get('selected_concept_id')}")
        print(f"Campaign Name: {parsed_json.get('campaign_name')}")
        print(f"Tagline: {parsed_json.get('campaign_strategy', {}).get('main_tagline')}")
        print(f"Number of Concepts: {len(parsed_json.get('generated_concepts', []))}")
        print(f"Number of Evaluations: {len(parsed_json.get('concept_evaluations', []))}")
        print(f"Visual Direction Colors: {[c.get('color_name') for c in parsed_json.get('campaign_strategy', {}).get('visual_direction', {}).get('colour_palette', [])]}")
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Response is not valid JSON: {e}")
        raise


if __name__ == "__main__":
    test_creative_director()
