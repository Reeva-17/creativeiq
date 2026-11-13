from app.ai.provider import LLMProvider
from app.core.exceptions import ProviderResponseError, ProviderUnavailableError
from app.schemas.brand_input import BrandInput
from app.schemas.brand_report import AudienceProfile, BrandDNA, EvidenceType, Finding, VisualIdentity


def f(statement: str, evidence_type: EvidenceType, rationale: str | None = None) -> Finding:
    return Finding(statement=statement, evidence_type=evidence_type, rationale=rationale)


class BrandAnalysisService:
    def __init__(self, provider: LLMProvider): self.provider = provider

    async def analyze(self, brand: BrandInput) -> tuple[BrandDNA, VisualIdentity, list[str]]:
        # Baseline is intentionally useful without an LLM and never asserts hidden facts.
        user = EvidenceType.user_provided
        assumptions: list[str] = []
        identity = [f(f"{brand.brand_name} operates in the {brand.industry} industry.", user)]
        if brand.business_description: identity.append(f(brand.business_description, user))
        else: assumptions.append("Business description was not supplied; no operational claims were inferred.")
        positioning = f(brand.positioning, user) if brand.positioning else None
        values = [f(v, user) for v in brand.brand_values]
        demographics = [f(brand.target_audience, user)] if brand.target_audience else []
        dna = BrandDNA(identity=identity, positioning=positioning, values=values, target_audience=AudienceProfile(demographics=demographics))
        visual = VisualIdentity()
        try:
            raw = await self.provider.generate_json(self._prompt(brand))
            ai_dna = BrandDNA.model_validate(self._normalise_dna(raw.get("brand_dna", {})))
            ai_visual = VisualIdentity.model_validate(raw.get("visual_identity", {}))
            # The prompt requires provenance, so validation protects the contract.
            dna = ai_dna.model_copy(update={"identity": identity + ai_dna.identity, "values": values + ai_dna.values, "positioning": positioning or ai_dna.positioning, "target_audience": dna.target_audience if demographics else ai_dna.target_audience})
            visual = ai_visual
        except (ProviderUnavailableError, ProviderResponseError, ValueError) as exc:
            assumptions.append(f"AI enrichment unavailable: {exc}")
        return dna, visual, assumptions

    @staticmethod
    def _normalise_dna(value: object) -> dict:
        """Accept a common provider variation without fabricating analytical data.

        The contract requires ``brand_dna`` to be an object. Some LLM responses
        return the otherwise-valid list of Finding objects directly. In that
        case those findings unambiguously describe identity, so retain them
        under ``identity`` rather than discarding the whole enrichment result.
        All other invalid shapes continue to fail validation and are reported in
        the response assumptions.
        """
        if isinstance(value, dict):
            return value
        if isinstance(value, list) and all(
            isinstance(item, dict) and "statement" in item and "evidence_type" in item
            for item in value
        ):
            return {"identity": value}
        return value  # Pydantic supplies the transparent validation error.

    def _prompt(self, brand: BrandInput) -> str:
        return "Analyze this brand. Return {brand_dna: ..., visual_identity: ...}; every Finding needs statement and evidence_type. Input: " + brand.model_dump_json()
