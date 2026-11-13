from app.schemas.brand_report import BrandDNA, CompetitorAnalysis, EvidenceType, Finding, SWOTAnalysis


class SWOTService:
    def generate(self, dna: BrandDNA, competitors: CompetitorAnalysis) -> SWOTAnalysis:
        strengths = dna.strengths[:]
        weaknesses = dna.weaknesses[:]
        opportunities = dna.opportunities[:]
        threats: list[Finding] = []
        if competitors.direct_competitors:
            threats.append(Finding(statement="Named direct competitors may compete for the same customer attention; sourced comparison is unavailable.", evidence_type=EvidenceType.ai_interpretation, rationale="Competitor names were user-supplied."))
        return SWOTAnalysis(strengths=strengths, weaknesses=weaknesses, opportunities=opportunities, threats=threats)
