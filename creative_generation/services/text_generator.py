
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.6-flash"

def generate_marketing_text(campaign_brief):

    if not API_KEY:
        raise ValueError("Gemini API key not found in .env")

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODEL}:generateContent"
    )

    prompt = f"""
    You are an expert marketing copywriter.

    Create marketing content for this campaign:

    {campaign_brief}

    Generate:
    1. Three catchy headlines
    2. One Instagram caption
    3. One brand tagline
    4. Five relevant hashtags
    5. One call-to-action

    Make the content creative, engaging and brand-appropriate.
    """

    response = requests.post(
        url,
        headers={
            "x-goog-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]
