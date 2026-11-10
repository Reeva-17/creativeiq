
import os
import base64
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load credentials from the main project .env file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

MODEL = "@cf/black-forest-labs/flux-1-schnell"

GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def generate_image(prompt: str):

    if not ACCOUNT_ID or not API_TOKEN:
        raise ValueError("Cloudflare credentials are missing from .env")

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{ACCOUNT_ID}/ai/run/{MODEL}"
    )

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "steps": 4
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    data = response.json()
    result = data.get("result", {})

    # Cloudflare returns the generated image as Base64
    if isinstance(result, dict):
        image_base64 = result.get("image")
    elif isinstance(result, str):
        image_base64 = result
    else:
        image_base64 = None

    if not image_base64:
        raise ValueError("No image was returned by Cloudflare")

    image_bytes = base64.b64decode(image_base64)

    filename = f"creative_{uuid.uuid4().hex}.png"
    image_path = GENERATED_DIR / filename

    with open(image_path, "wb") as image_file:
        image_file.write(image_bytes)

    return image_path
