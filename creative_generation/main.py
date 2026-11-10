
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from creative_generation.services.text_generator import generate_marketing_text

app = FastAPI(title="CampaignOS Creative Generation API")

class CampaignRequest(BaseModel):
    brief: str

@app.get("/")
def home():
    return {"message": "CampaignOS is running!"}

@app.post("/generate-text")
def generate_text(request: CampaignRequest):
    try:
        result = generate_marketing_text(request.brief)
        return {"generated_content": result}

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
