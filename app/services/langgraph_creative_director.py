import json
from pathlib import Path
from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, START, END

from app.schemas.campaign_schema import (
    CampaignInput,
    CampaignConcept,
    ConceptEvaluation,
    CampaignRationale,
    MasterCampaignStrategy,
    CreativeDirectorHandoff
)
from app.services.creative_director import concept_ideation_engine
from app.services.campaign_evaluator import autonomous_campaign_evaluator
from app.services.campaign_strategy import campaign_strategy_synthesizer
from app.services.creative_brief_generator import generate_markdown_creative_brief
from app.core.config import settings


class CreativeDirectorState(TypedDict, total=False):
    campaign_input: CampaignInput
    concepts: List[CampaignConcept]
    evaluations: List[ConceptEvaluation]
    rationale: CampaignRationale
    winning_concept: CampaignConcept
    strategy: MasterCampaignStrategy
    creative_brief_markdown: str
    final_handoff: CreativeDirectorHandoff


def input_refinement_node(state: CreativeDirectorState) -> Dict[str, Any]:
    """Node 1: Validate and frame input context."""
    c_input = state["campaign_input"]
    print(f"\n[LangGraph · Step 1/5] Analyzing brand intelligence & framing objectives for '{c_input.brand_name}'...")
    return {"campaign_input": c_input}


def concept_ideation_node(state: CreativeDirectorState) -> Dict[str, Any]:
    """Node 2: Generate 3 diverse creative campaign concepts."""
    c_input = state["campaign_input"]
    print(f"[LangGraph · Step 2/5] Ideating 3 distinct creative concepts for '{c_input.brand_name}'...")
    concepts = concept_ideation_engine.generate_concepts(c_input)
    print(f" -> Generated 3 concepts: {[c.concept_name for c in concepts]}")
    return {"concepts": concepts}


def autonomous_evaluation_node(state: CreativeDirectorState) -> Dict[str, Any]:
    """Node 3: Autonomously evaluate concepts and select the winner with rationale."""
    c_input = state["campaign_input"]
    concepts = state["concepts"]
    print(f"[LangGraph · Step 3/5] Autonomously evaluating concepts across 4-criteria rubric...")
    evaluations, rationale, winning_concept = autonomous_campaign_evaluator.evaluate_and_decide(c_input, concepts)
    print(f" -> Winner Selected: {winning_concept.concept_id} ('{winning_concept.concept_name}')")
    return {
        "evaluations": evaluations,
        "rationale": rationale,
        "winning_concept": winning_concept
    }


def strategy_synthesis_node(state: CreativeDirectorState) -> Dict[str, Any]:
    """Node 4: Synthesize full campaign strategy, visual direction, and Instagram platform execution."""
    c_input = state["campaign_input"]
    winner = state["winning_concept"]
    print(f"[LangGraph · Step 4/5] Developing master strategy, visual direction, and Instagram platform execution...")
    strategy = campaign_strategy_synthesizer.synthesize_strategy(c_input, winner)
    print(f" -> Strategy Formulated: '{strategy.campaign_name}' | Tagline: '{strategy.main_tagline}'")
    return {"strategy": strategy}


def handoff_packaging_node(state: CreativeDirectorState) -> Dict[str, Any]:
    """Node 5: Package structured handoff JSON and Markdown Creative Brief for Person 3."""
    c_input = state["campaign_input"]
    concepts = state["concepts"]
    evaluations = state["evaluations"]
    rationale = state["rationale"]
    strategy = state["strategy"]

    print(f"[LangGraph · Step 5/5] Packaging Person 3 handoff blueprint and creative brief...")
    brief_md = generate_markdown_creative_brief(
        campaign_input=c_input,
        concepts=concepts,
        evaluations=evaluations,
        rationale=rationale,
        strategy=strategy
    )

    handoff = CreativeDirectorHandoff(
        brand_name=c_input.brand_name,
        industry=c_input.industry,
        campaign_name=strategy.campaign_name,
        selected_concept_id=rationale.selected_concept_id,
        generated_concepts=concepts,
        concept_evaluations=evaluations,
        campaign_rationale=rationale,
        campaign_strategy=strategy,
        creative_brief_markdown=brief_md
    )

    # Save artifacts to outputs/
    safe_name = c_input.brand_name.lower().replace(" ", "_").replace("/", "_")
    output_dir = settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{safe_name}_campaign_blueprint.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(handoff.model_dump_json(indent=2))

    md_path = output_dir / f"{safe_name}_creative_brief.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(brief_md)

    print(f" -> Saved Person 3 JSON Blueprint: {json_path}")
    print(f" -> Saved Markdown Creative Brief: {md_path}")

    return {
        "creative_brief_markdown": brief_md,
        "final_handoff": handoff
    }


def build_creative_director_graph() -> StateGraph:
    """Build the compiled LangGraph workflow."""
    workflow = StateGraph(CreativeDirectorState)

    workflow.add_node("input_refinement", input_refinement_node)
    workflow.add_node("concept_ideation", concept_ideation_node)
    workflow.add_node("autonomous_evaluation", autonomous_evaluation_node)
    workflow.add_node("strategy_synthesis", strategy_synthesis_node)
    workflow.add_node("handoff_packaging", handoff_packaging_node)

    workflow.add_edge(START, "input_refinement")
    workflow.add_edge("input_refinement", "concept_ideation")
    workflow.add_edge("concept_ideation", "autonomous_evaluation")
    workflow.add_edge("autonomous_evaluation", "strategy_synthesis")
    workflow.add_edge("strategy_synthesis", "handoff_packaging")
    workflow.add_edge("handoff_packaging", END)

    return workflow.compile()


class AutonomousCreativeDirectorAgent:
    """
    Person 2 — Autonomous Creative Director Agent.
    Orchestrates the entire creative strategy and decision-making pipeline via LangGraph.
    """

    def __init__(self):
        self.app = build_creative_director_graph()

    def run(self, campaign_input: CampaignInput) -> CreativeDirectorHandoff:
        """Execute the full Creative Director agent pipeline."""
        initial_state: CreativeDirectorState = {"campaign_input": campaign_input}
        final_state = self.app.invoke(initial_state)
        return final_state["final_handoff"]

    def run_from_person1_report(
        self,
        report_data: Dict[str, Any],
        product_name: Optional[str] = None,
        product_description: Optional[str] = None,
        campaign_objective: Optional[str] = None,
        budget: Optional[str] = None,
        duration: Optional[str] = "30 Days"
    ) -> CreativeDirectorHandoff:
        """Adapter to execute directly from Person 1's BrandIntelligenceReport."""
        c_input = CampaignInput.from_person_1_report(
            report=report_data,
            product_name=product_name,
            product_description=product_description,
            campaign_objective=campaign_objective,
            budget=budget,
            duration=duration,
        )
        return self.run(c_input)


autonomous_creative_director = AutonomousCreativeDirectorAgent()
