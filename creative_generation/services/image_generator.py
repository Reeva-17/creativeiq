
import os
import base64
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load credentials from the main project .env file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"

GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


class ImageGenerationError(RuntimeError):
    """A provider error safe to return to the browser without exposing secrets."""


def _cloudflare_error(response: requests.Response) -> str:
    """Keep Cloudflare's useful error messages instead of hiding them in HTTPError."""
    try:
        payload = response.json()
        errors = payload.get("errors") or payload.get("messages") or []
        detail = "; ".join(
            str(item.get("message", item)) if isinstance(item, dict) else str(item)
            for item in errors
        )
        if detail:
            return detail
    except ValueError:
        pass
    return response.text[:500] or response.reason


def generate_image(prompt: str):
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    model = os.getenv("CLOUDFLARE_IMAGE_MODEL", DEFAULT_MODEL)

    if not account_id or not api_token:
        raise ValueError("Cloudflare credentials are missing from .env")
    if not prompt.strip():
        raise ValueError("Image prompt cannot be empty")
    if len(prompt) > 2048:
        raise ValueError("Image prompt exceeds the Cloudflare FLUX 2,048-character limit")

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{account_id}/ai/run/{model}"
    )

    headers = {
        "Authorization": f"Bearer {api_token}",
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

    if not response.ok:
        raise ImageGenerationError(
            f"Cloudflare Workers AI rejected the image request ({response.status_code}): "
            f"{_cloudflare_error(response)}. Check CLOUDFLARE_IMAGE_MODEL, your account's Workers AI access, and token permissions."
        )

    data = response.json()
    if not data.get("success", True):
        raise ImageGenerationError(f"Cloudflare Workers AI returned an unsuccessful response: {_cloudflare_error(response)}")
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
