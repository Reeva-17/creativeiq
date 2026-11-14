"""Convert a user's one-prompt campaign request into Person 1's strict contract."""
from app.ai.llm_gateway import llm_gateway
from app.schemas.brand_input import BrandInput


def brand_from_prompt(prompt: str) -> BrandInput:
    response = llm_gateway.generate_json(
        f"""Extract a brand brief from this user request. Do not invent claims.
Return JSON matching this structure only:
{{
  "brand_name": "...", "industry": "...", "business_description": "...",
  "products_services": ["..."], "target_audience": "...",
  "positioning": "...", "brand_values": ["..."],
  "additional_information": "..."
}}
User request:\n{prompt}""",
        system_prompt="You are a precise brand-intake assistant. Return only valid JSON.",
        max_tokens=1200,
    )
    return BrandInput.model_validate(response)
