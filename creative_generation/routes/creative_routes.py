
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from creative_generation.services.text_generator import generate_marketing_text
from creative_generation.services.image_generator import generate_image
from creative_generation.services.poster_generator import generate_poster


router = APIRouter()


# ---------------- REQUEST MODELS ----------------

class CampaignRequest(BaseModel):
    brief: str


class ImageRequest(BaseModel):
    prompt: str


class CreativeRequest(BaseModel):
    brief: str


class PosterRequest(BaseModel):
    prompt: str
    brand_name: str
    headline: str
    offer: str
    cta: str


# ---------------- HOME ROUTE ----------------

@router.get("/")
def home():
    return {
        "message": "CampaignOS Creative Generation API is running!"
    }


# ---------------- HEALTH CHECK ----------------

@router.get("/health")
def health():
    return {
        "status": "healthy",
        "module": "Creative Generation"
    }


# ---------------- TEXT GENERATION ----------------

@router.post("/generate-text")
def generate_text(request: CampaignRequest):
    try:
        result = generate_marketing_text(request.brief)

        return {
            "success": True,
            "generated_content": result
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ---------------- IMAGE GENERATION ----------------

@router.post("/generate-image")
def create_image(request: ImageRequest):
    try:
        image_path = generate_image(request.prompt)

        return {
            "success": True,
            "message": "Image generated successfully!",
            "image_url": f"/generated/{image_path.name}"
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ---------------- COMBINED CREATIVE GENERATION ----------------

@router.post("/generate-creative")
def generate_complete_creative(request: CreativeRequest):
    try:
        # Generate marketing text using Gemini
        text_result = generate_marketing_text(request.brief)

        # Create image prompt
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

        # Generate image using Cloudflare
        image_path = generate_image(image_prompt)

        return {
            "success": True,
            "campaign_text": text_result,
            "image_url": f"/generated/{image_path.name}"
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ---------------- POSTER GENERATION ----------------

@router.post("/generate-poster")
def create_poster(request: PosterRequest):
    try:
        # Generate background image
        image_path = generate_image(request.prompt)

        # Create complete poster
        poster_path = generate_poster(
            image_path=image_path,
            brand_name=request.brand_name,
            headline=request.headline,
            offer=request.offer,
            cta=request.cta
        )

        return {
            "success": True,
            "message": "Poster generated successfully!",
            "poster_url": f"/generated/{poster_path.name}"
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
