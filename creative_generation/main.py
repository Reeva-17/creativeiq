
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from creative_generation.services.text_generator import generate_marketing_text
from creative_generation.services.image_generator import generate_image


# Initialize FastAPI
app = FastAPI(
    title="CampaignOS Creative Generation API",
    description="AI-powered marketing text and image generation",
    version="1.0.0"
)


# Create folder to store generated images
GENERATED_DIR = Path(__file__).parent / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


# Make generated images accessible through URLs
app.mount(
    "/generated",
    StaticFiles(directory=GENERATED_DIR),
    name="generated"
)


# Request models
class CampaignRequest(BaseModel):
    brief: str


class ImageRequest(BaseModel):
    prompt: str


# Home route
@app.get("/")
def home():
    return {
        "message": "CampaignOS Creative Generation API is running!"
    }


# Health check route
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "module": "Creative Generation"
    }


# Gemini AI text generation
@app.post("/generate-text")
def generate_text(request: CampaignRequest):
    try:
        result = generate_marketing_text(request.brief)

        return {
            "success": True,
            "generated_content": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# Cloudflare AI image generation
@app.post("/generate-image")
def create_image(request: ImageRequest):
    try:
        image_path = generate_image(request.prompt)

        return {
            "success": True,
            "message": "Image generated successfully!",
            "image_url": f"/generated/{image_path.name}"
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

# Combined campaign creative generation

class CreativeRequest(BaseModel):
    brief: str


@app.post("/generate-creative")
def generate_complete_creative(request: CreativeRequest):
    try:
        # Step 1: Generate marketing text using Gemini
        text_result = generate_marketing_text(request.brief)

        # Step 2: Create an image prompt from the campaign brief
        image_prompt = f"""
        Create a professional marketing advertisement image
        based on this campaign:

        {request.brief}

        Requirements:
        - High-quality commercial advertising photography
        - Attractive and professional composition
        - Visually appealing colors
        - Suitable for social media marketing
        - No text, logos or watermarks
        """

        # Step 3: Generate campaign image using Cloudflare
        image_path = generate_image(image_prompt)

        # Step 4: Return both results together
        return {
            "success": True,
            "campaign_text": text_result,
            "image_url": f"/generated/{image_path.name}"
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


