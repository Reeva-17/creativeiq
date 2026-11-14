from typing import List, Dict, Any
from app.ai.llm_gateway import llm_gateway, LLMGateway
from app.schemas.campaign_schema import CampaignInput, CampaignConcept


class ConceptIdeationEngine:
    """
    Campaign Ideation Brain for Person 2.
    Generates exactly 3 distinct, strategically differentiated creative campaign concepts
    tailored to the brand's identity, target audience tensions, and competitor white spaces.
    """

    def __init__(self, gateway: LLMGateway = llm_gateway):
        self.gateway = gateway

    def generate_concepts(self, campaign_input: CampaignInput) -> List[CampaignConcept]:
        """Generate 3 distinct creative concepts."""
        system_prompt = (
            "You are CREATIVEIQ's Executive Creative Director. "
            "You do not write superficial taglines or cliché marketing slogans. "
            "You engineer bold, strategically sound advertising campaigns that captivate audiences, "
            "differentiate sharply from competitors, and drive real business outcomes."
        )

        prompt = f"""
BRAND & CAMPAIGN CONTEXT:
- Brand Name: {campaign_input.brand_name}
- Industry: {campaign_input.industry}
- Product / Service: {campaign_input.product_name} - {campaign_input.product_description}
- Target Audience & Pain Points: {campaign_input.target_audience}
- Primary Campaign Objective: {campaign_input.campaign_objective}
- Specific Objectives: {campaign_input.campaign_objectives}
- Brand Tone & Values: {campaign_input.brand_tone or 'Authentic, High-Impact'} | DNA: {campaign_input.brand_dna}
- Competitors: {campaign_input.competitors}
- Competitor Gaps / White Space: {campaign_input.market_gaps}
- Campaign Duration: {campaign_input.campaign_duration}
- Campaign Budget: {campaign_input.campaign_budget or 'Standard Growth Budget'}

TASK:
Develop exactly THREE distinct, original creative campaign concepts.
Each concept MUST represent a completely different strategic and creative angle:
1. Concept 1 (CONCEPT_1): Emotion & Storytelling driven — focuses on human vulnerability, identity, or deep emotional transformation.
2. Concept 2 (CONCEPT_2): Bold & Disruptive / Culture-Jacking — subverts category clichés, uses high-energy provocative messaging, or challenges competitors directly.
3. Concept 3 (CONCEPT_3): Community, Values & Lifestyle / Utility — elevates social connection, shared purpose, daily ritual, or sustainable habit formation.

CRITICAL REQUIREMENTS:
- Give each concept an evocative concept_name (e.g., 'Skin Unfiltered', 'Reclaim the Pour', 'The 4PM Pause').
- The main_tagline must be punchy, memorable, and culture-ready.
- The big_creative_idea must clearly articulate the narrative thesis.
- Provide 3 distinct scroll-stopping social media content_hooks for each concept.
- Highlight the unique_angle_vs_competitors and how it avoids competitor clichés.

Return your output as a JSON object with this exact structure:
{{
  "concepts": [
    {{
      "concept_id": "CONCEPT_1",
      "concept_name": "...",
      "main_tagline": "...",
      "big_creative_idea": "...",
      "creative_angle": "Emotional & Storytelling",
      "target_audience_focus": "...",
      "emotional_positioning": "...",
      "key_marketing_message": "...",
      "unique_angle_vs_competitors": "...",
      "content_hooks": ["Hook 1", "Hook 2", "Hook 3"],
      "visual_hook_teaser": "..."
    }},
    {{
      "concept_id": "CONCEPT_2",
      "concept_name": "...",
      "main_tagline": "...",
      "big_creative_idea": "...",
      "creative_angle": "Bold & Disruptive",
      "target_audience_focus": "...",
      "emotional_positioning": "...",
      "key_marketing_message": "...",
      "unique_angle_vs_competitors": "...",
      "content_hooks": ["Hook 1", "Hook 2", "Hook 3"],
      "visual_hook_teaser": "..."
    }},
    {{
      "concept_id": "CONCEPT_3",
      "concept_name": "...",
      "main_tagline": "...",
      "big_creative_idea": "...",
      "creative_angle": "Community & Lifestyle Ritual",
      "target_audience_focus": "...",
      "emotional_positioning": "...",
      "key_marketing_message": "...",
      "unique_angle_vs_competitors": "...",
      "content_hooks": ["Hook 1", "Hook 2", "Hook 3"],
      "visual_hook_teaser": "..."
    }}
  ]
}}
"""
        response_dict = self.gateway.generate_json(
            prompt, system_prompt=system_prompt, max_tokens=2200
        )
        raw_concepts = response_dict.get("concepts", [])

        if len(raw_concepts) != 3:
            # If not exactly 3, attempt slicing or fallback
            if len(raw_concepts) > 3:
                raw_concepts = raw_concepts[:3]
            else:
                raise ValueError(f"Expected 3 concepts from LLM, received {len(raw_concepts)}")

        validated_concepts: List[CampaignConcept] = []
        for idx, c_data in enumerate(raw_concepts, start=1):
            c_data["concept_id"] = f"CONCEPT_{idx}"
            validated_concepts.append(CampaignConcept.model_validate(c_data))

        return validated_concepts


concept_ideation_engine = ConceptIdeationEngine()
creative_director = concept_ideation_engine

# Convenience alias for tests expecting AutonomousCreativeDirector
def get_autonomous_creative_director():
    from app.services.campaign_agent import AutonomousCreativeDirector
    return AutonomousCreativeDirector()

class AutonomousCreativeDirectorProxy:
    def __new__(cls, *args, **kwargs):
        from app.services.campaign_agent import AutonomousCreativeDirector
        return AutonomousCreativeDirector(*args, **kwargs)

AutonomousCreativeDirector = AutonomousCreativeDirectorProxy
