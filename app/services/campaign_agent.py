from typing import Dict, Any, Optional
from app.schemas.campaign_schema import CampaignInput, CreativeDirectorHandoff
from app.services.langgraph_creative_director import autonomous_creative_director


class CreativeIQCampaignAgent:
    """Wrapper matching the Creative Director agent interface."""

    def __init__(self):
        self.agent = autonomous_creative_director

    def generate_campaign(self, campaign_input: CampaignInput) -> CreativeDirectorHandoff:
        return self.agent.run(campaign_input)

    def generate_campaign_blueprint(self, person_1_output: Optional[Dict[str, Any]] = None) -> str:
        """Fallback method for tests expecting string/dict output."""
        if person_1_output is None:
            # Fallback mock brand input
            mock_input = CampaignInput(
                brand_name="EcoGlow",
                industry="Sustainable Consumer Goods",
                product_name="EcoGlow Smart Hydration Bottle",
                product_description="An intelligent reusable bottle tracking daily hydration and calculating plastic bottles saved.",
                target_audience="Urban professionals and college students aged 18-32 focused on sustainability and daily wellness.",
                campaign_objective="Drive awareness of sustainable hydration habits and boost direct-to-consumer bottle sales.",
                campaign_objectives=[
                    "Increase Brand Awareness by 45%",
                    "Drive 25,000 Social Engagements",
                    "Achieve 3.5x ROAS on Instagram Ads"
                ],
                brand_tone="Empowering, Minimalist, Forward-Thinking",
                campaign_budget="$25,000",
                campaign_duration="30 Days"
            )
            result = self.agent.run(mock_input)
            return result.model_dump_json(indent=2)
        else:
            result = self.agent.run_from_person1_report(person_1_output)
            return result.model_dump_json(indent=2)


campaign_agent = CreativeIQCampaignAgent()
AutonomousCreativeDirector = CreativeIQCampaignAgent
