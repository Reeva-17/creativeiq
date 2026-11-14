
"""Gemini-backed copy generation for Person 3."""
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-3.8-flash"


class TextGenerationError(RuntimeError):
    """A safe, actionable Person 3 provider failure."""


def _provider_error(response):
    try:
        error = response.json().get("error", {})
        return str(error.get("message") or error)
    except ValueError:
        return response.text[:500] or response.reason


def generate_marketing_text(campaign_brief):
    """Generate copy, retrying transient timeout, rate-limit, and 5xx errors."""
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    timeout_seconds = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "90"))
    max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "2"))
    if not api_key:
        raise TextGenerationError("GEMINI_API_KEY is missing from the environment")

    prompt = (
        "You are an expert marketing copywriter. Create marketing content for this campaign:\n\n"
        + campaign_brief
        + "\n\nGenerate three catchy headlines, one Instagram caption, one brand tagline, "
        "five relevant hashtags, and one call-to-action. Keep it creative, engaging, and brand-appropriate."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    last_error = "unknown error"

    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                url,
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=timeout_seconds,
            )
            if response.ok:
                try:
                    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError, TypeError, ValueError) as exc:
                    raise TextGenerationError("Gemini returned no usable marketing text") from exc
                if isinstance(text, str) and text.strip():
                    return text
                raise TextGenerationError("Gemini returned empty marketing text")

            last_error = f"Gemini returned HTTP {response.status_code}: {_provider_error(response)}"
            if response.status_code != 429 and response.status_code < 500:
                raise TextGenerationError(last_error)
        except requests.Timeout:
            last_error = f"Gemini timed out after {timeout_seconds:g} seconds"
        except requests.RequestException as exc:
            last_error = f"Gemini network request failed: {exc}"

        if attempt < max_retries:
            time.sleep(2 ** attempt)

    # Gemini can be temporarily quota-limited or congested.  Use the existing
    # configured Groq integration for genuine AI copy before failing a campaign;
    # never substitute fixed/template marketing output.
    try:
        from app.ai.llm_gateway import LLMGateway

        groq_gateway = LLMGateway(preferred_provider="groq")
        return groq_gateway.generate(
            prompt,
            system_prompt="You are an expert marketing copywriter. Return polished campaign copy only.",
            max_tokens=1200,
        )
    except Exception as fallback_exc:
        raise TextGenerationError(
            "Person 3 text generation failed through Gemini and Groq. "
            f"Gemini: {last_error}; Groq: {fallback_exc}"
        ) from fallback_exc
