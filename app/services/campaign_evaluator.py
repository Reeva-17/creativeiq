from typing import List, Tuple, Dict, Any
from app.ai.llm_gateway import llm_gateway, LLMGateway
from app.schemas.campaign_schema import (
    CampaignInput,
    CampaignConcept,
    ConceptEvaluation,
    EvaluationCriteriaScores,
    CampaignRationale
)


class AutonomousCampaignEvaluator:
    """
    Autonomous Decision-Making Engine for Person 2.
    Evaluates generated concepts against a multi-dimensional rubric,
    calculates objective weighted scores locally, selects the winning concept,
    and produces an executive strategic rationale detailing why alternatives were rejected.
    """

    def __init__(self, gateway: LLMGateway = llm_gateway):
        self.gateway = gateway
        # Equal 25% weight across the 4 primary criteria mandated by requirements
        self.weights = {
            "creativity": 0.25,
            "audience_relevance": 0.25,
            "brand_consistency": 0.25,
            "campaign_objectives_alignment": 0.25,
        }

    def evaluate_and_decide(
        self,
        campaign_input: CampaignInput,
        concepts: List[CampaignConcept]
    ) -> Tuple[List[ConceptEvaluation], CampaignRationale, CampaignConcept]:
        """
        Evaluate all 3 concepts, determine the winning concept, and synthesize rationale.
        Returns (evaluations, rationale, winning_concept).
        """
        system_prompt = (
            "You are CREATIVEIQ's Chief Evaluation Officer and Autonomous Decision-Making Agent. "
            "You perform rigorous, unbiased, and critical evaluations of advertising concepts. "
            "You do not give uniform scores; you ruthlessly assess trade-offs, market viability, "
            "brand authenticity, and conversion friction."
        )

        concepts_summary = [c.model_dump() for c in concepts]

        prompt = f"""
BRAND BRIEF:
- Brand Name: {campaign_input.brand_name}
- Industry: {campaign_input.industry}
- Product: {campaign_input.product_name}
- Target Audience: {campaign_input.target_audience}
- Campaign Objectives: {campaign_input.campaign_objectives or [campaign_input.campaign_objective]}
- Brand DNA / Tone: {campaign_input.brand_tone} | Values: {campaign_input.brand_dna.get('values', [])}
- Competitors & Market Gaps: {campaign_input.competitors} | White Spaces: {campaign_input.market_gaps}

THREE CONCEPTS TO EVALUATE:
{concepts_summary}

EVALUATION RUBRIC (Score each criterion strictly between 1.0 and 10.0):
1. creativity: Freshness, narrative originality, breakthrough ability in a crowded feed.
2. audience_relevance: Resonance with real target audience anxieties, aspirations, and habits.
3. brand_consistency: Faithfulness to Brand DNA, voice, and authentic capabilities (not overpromising).
4. campaign_objectives_alignment: Direct power to hit stated marketing KPIs (awareness, CTR, conversions).
5. feasibility: Ease of production and platform rollout within budget and timeline.
6. impact_potential: Scalability, virality, and organic community talkability.

TASK:
1. Score each concept on all 6 parameters.
2. Provide at least 2 distinct strengths and 2 distinct weaknesses for each concept.
3. Suggest 2 actionable improvements for each concept.
4. Write a comprehensive evaluation_summary for each.
5. Select the SINGLE BEST concept as the winner. Mark its selection_status as 'selected'. Mark the other two as 'rejected'.
6. Formulate an exhaustive campaign rationale:
   - Explain why the winner triumphed.
   - For each rejected concept, give a specific comparative critique explaining why it lost.
   - Explain how the winner aligns with Brand DNA, fills competitor white space, and guarantees objective delivery.

Return JSON in this exact structure:
{{
  "evaluations": [
    {{
      "concept_id": "CONCEPT_1",
      "scores": {{
        "creativity": 8.5,
        "audience_relevance": 9.0,
        "brand_consistency": 9.2,
        "campaign_objectives_alignment": 8.8,
        "feasibility": 8.5,
        "impact_potential": 8.7
      }},
      "strengths": ["...", "..."],
      "weaknesses": ["...", "..."],
      "improvement_suggestions": ["...", "..."],
      "evaluation_summary": "...",
      "selection_status": "rejected"
    }},
    {{
      "concept_id": "CONCEPT_2",
      "scores": {{
        "creativity": 9.5,
        "audience_relevance": 8.8,
        "brand_consistency": 8.9,
        "campaign_objectives_alignment": 9.3,
        "feasibility": 8.8,
        "impact_potential": 9.4
      }},
      "strengths": ["...", "..."],
      "weaknesses": ["...", "..."],
      "improvement_suggestions": ["...", "..."],
      "evaluation_summary": "...",
      "selection_status": "selected"
    }},
    {{
      "concept_id": "CONCEPT_3",
      "scores": {{
        "creativity": 8.0,
        "audience_relevance": 8.4,
        "brand_consistency": 8.7,
        "campaign_objectives_alignment": 8.2,
        "feasibility": 9.0,
        "impact_potential": 8.0
      }},
      "strengths": ["...", "..."],
      "weaknesses": ["...", "..."],
      "improvement_suggestions": ["...", "..."],
      "evaluation_summary": "...",
      "selection_status": "rejected"
    }}
  ],
  "rationale": {{
    "selected_concept_id": "CONCEPT_2",
    "selection_verdict": "...",
    "why_selected_over_alternatives": {{
      "CONCEPT_1": "Why Concept 1 fell short...",
      "CONCEPT_3": "Why Concept 3 fell short..."
    }},
    "brand_dna_alignment": "...",
    "competitor_white_space": "...",
    "objective_delivery": "..."
  }}
}}
"""
        response_dict = self.gateway.generate_json(prompt, system_prompt=system_prompt)
        raw_evaluations = response_dict.get("evaluations", [])
        raw_rationale = response_dict.get("rationale", {})

        # Validate and compute weighted overall scores locally
        evaluations_dict: Dict[str, ConceptEvaluation] = {}
        for item in raw_evaluations:
            c_id = item["concept_id"]
            scores_data = item["scores"]

            # Local calculation using strict 4-criteria weights + minor impact factor
            weighted_score = (
                scores_data["creativity"] * self.weights["creativity"] +
                scores_data["audience_relevance"] * self.weights["audience_relevance"] +
                scores_data["brand_consistency"] * self.weights["brand_consistency"] +
                scores_data["campaign_objectives_alignment"] * self.weights["campaign_objectives_alignment"]
            )
            item["overall_score"] = round(weighted_score, 2)
            eval_obj = ConceptEvaluation.model_validate(item)
            evaluations_dict[c_id] = eval_obj

        # Determine winner: pick the one marked 'selected' or the highest score if ambiguous
        selected_candidates = [e for e in evaluations_dict.values() if e.selection_status == "selected"]
        if len(selected_candidates) == 1:
            winner_eval = selected_candidates[0]
        else:
            # Fallback to absolute highest overall score
            winner_eval = max(evaluations_dict.values(), key=lambda e: e.overall_score)
            for cid, e in evaluations_dict.items():
                e.selection_status = "selected" if cid == winner_eval.concept_id else "rejected"

        winning_id = winner_eval.concept_id
        winning_concept = next((c for c in concepts if c.concept_id == winning_id), concepts[0])

        # Ensure rationale selected ID matches
        raw_rationale["selected_concept_id"] = winning_id
        if "why_selected_over_alternatives" not in raw_rationale or not isinstance(raw_rationale["why_selected_over_alternatives"], dict):
            raw_rationale["why_selected_over_alternatives"] = {
                c.concept_id: f"{winning_concept.concept_name} presented superior engagement metrics and sharper differentiation."
                for c in concepts if c.concept_id != winning_id
            }

        rationale = CampaignRationale.model_validate(raw_rationale)
        return list(evaluations_dict.values()), rationale, winning_concept


autonomous_campaign_evaluator = AutonomousCampaignEvaluator()
