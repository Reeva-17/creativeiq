
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes import brand, competitors, campaign, workflow
from app.core.config import settings

from creative_generation.routes.creative_routes import (
    router as creative_router
)

from critic_optimizer.main import app as critic_app


app = FastAPI(
    title="CREATIVEIQ · Autonomous Marketing Multi-Agent System",
    version="2.0.0",
    description=(
        "Unified AI-powered marketing platform combining "
        "Brand Intelligence, Autonomous Creative Direction, "
        "Creative Generation and Critic & Optimizer."
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PERSON 1 — BRAND INTELLIGENCE
app.include_router(brand.router)
app.include_router(competitors.router)


# PERSON 2 — AUTONOMOUS CREATIVE DIRECTOR
app.include_router(campaign.router)
app.include_router(workflow.router)


# RASHI — CREATIVE GENERATION
app.include_router(
    creative_router,
    prefix="/api/v1/creative",
    tags=["Creative Generation"]
)


# REEVA — CRITIC & OPTIMIZER
app.mount("/api/v1/critic", critic_app)


# GENERATED IMAGES AND POSTERS
GENERATED_DIR = (
    Path(__file__).resolve().parent.parent
    / "creative_generation"
    / "generated"
)
WEB_DIR = Path(__file__).resolve().parent / "static"

GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/generated",
    StaticFiles(directory=GENERATED_DIR),
    name="generated"
)


@app.get("/", tags=["System"], summary="CreativeIQ API entry point")
async def root():
    """Serve the one-prompt CreativeIQ browser experience."""
    return FileResponse(WEB_DIR / "index.html")


# UNIFIED HEALTH CHECK
@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "service": "CREATIVEIQ",
        "person_1": "Brand Intelligence",
        "person_2": "Autonomous Creative Director",
        "person_3": "Creative Generation",
        "person_4": "Critic & Optimizer"
    }
