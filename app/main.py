from fastapi import FastAPI
from app.api.routes import brand, competitors, campaign

app = FastAPI(
    title="CREATIVEIQ · Autonomous Marketing Multi-Agent System",
    version="2.0.0",
    description=(
        "**CREATIVEIQ Brain & Execution Architecture**\n\n"
        "- **Person 1 (Brand Intelligence Agent)**: Evidence-labelled brand DNA, transparent competitor research, and SWOT analysis.\n"
        "- **Person 2 (Autonomous Creative Director Agent)**: Multi-concept ideation, autonomous decision-making matrix, master campaign strategy, visual direction blueprint, and Instagram platform execution.\n"
        "- **Person 3 Handoff**: Strictly validated JSON and Markdown Creative Brief ready for downstream creative production."
    )
)

# Person 1 Routes
app.include_router(brand.router)
app.include_router(competitors.router)

# Person 2 Routes
app.include_router(campaign.router)


@app.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "system": "CREATIVEIQ Multi-Agent Platform",
        "person_1_module": "Brand Intelligence Agent (v1.0.0)",
        "person_2_module": "Autonomous Creative Director Agent (v2.0.0)",
        "person_3_contract": "Compatible with Downstream Asset Generation"
    }
