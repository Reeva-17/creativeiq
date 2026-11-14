import os
import time
from dotenv import load_dotenv
from google import genai

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

load_dotenv(os.path.join(ROOT_DIR, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def get_gemini_client():
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    return genai.Client(api_key=API_KEY)


def generate_ai_evaluation(prompt: str) -> str:
    client = get_gemini_client()

    for attempt in range(1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response")

            return response.text

        except Exception as e:
            error_message = str(e)

            if ("503" in error_message or "UNAVAILABLE" in error_message
                    or "429" in error_message or "RESOURCE_EXHAUSTED" in error_message):
                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue

            raise

    raise RuntimeError("Gemini evaluation failed after retries")
