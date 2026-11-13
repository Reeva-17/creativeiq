
from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from creative_generation.routes.creative_routes import router


# Initialize FastAPI
app = FastAPI(
    title="CampaignOS Creative Generation API",
    description="AI-powered marketing text, image and poster generation",
    version="1.0.0"
)


# Generated files folder
GENERATED_DIR = Path(__file__).parent / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


# Serve generated images and posters
app.mount(
    "/generated",
    StaticFiles(directory=GENERATED_DIR),
    name="generated"
)


# Register all API routes
app.include_router(router)
