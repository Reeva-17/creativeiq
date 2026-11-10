from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes import brand, competitors
from creative_generation.routes.creative_routes import router as creative_router
from critic_optimizer.main import app as critic_app

app = FastAPI(
    title="CreativeIQ",
    description="Unified AI-powered brand intelligence, creative generation and optimization platform",
    version="1.0.0"
)

# Brand Intelligence
app.include_router(brand.router)
app.include_router(competitors.router)

# Creative Generation
app.include_router(
    creative_router,
    prefix="/api/v1/creative",
    tags=["Creative Generation"]
)

# Critic & Optimizer
app.mount("/api/v1/critic", critic_app)

# Generated images
GENERATED_DIR = Path(__file__).resolve().parent.parent / "creative_generation" / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/generated",
    StaticFiles(directory=GENERATED_DIR),
    name="generated"
)

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "service": "CreativeIQ"
    }