import asyncio
import json
from typing import Any

from groq import AsyncGroq

from app.ai.provider import LLMProvider
from app.core.exceptions import ProviderResponseError, ProviderUnavailableError


class GroqProvider(LLMProvider):
    """Groq SDK adapter; the rest of the application depends only on LLMProvider."""

    def __init__(self, api_key: str | None, model: str, timeout: float = 20, retries: int = 2, client: Any | None = None):
        self.api_key, self.model, self.timeout, self.retries = api_key, model, timeout, retries
        # Disable SDK retries so that the application's retry policy is predictable and testable.
        self.client = client or (AsyncGroq(api_key=api_key, timeout=timeout, max_retries=0) if api_key else None)

    async def generate_json(self, prompt: str) -> dict[str, Any]:
        if not self.api_key or not self.client:
            raise ProviderUnavailableError("GROQ_API_KEY is not configured")
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Return only a JSON object. Do not include Markdown or commentary."},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                content = completion.choices[0].message.content
                decoded = json.loads(content or "")
                if not isinstance(decoded, dict):
                    raise ValueError("response is not a JSON object")
                return decoded
            except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as exc:
                # A malformed model answer cannot be recovered by pretending it is valid.
                last_error = exc
            except Exception as exc:  # Groq SDK timeout, transport, rate-limit, and API errors
                last_error = exc
            if attempt < self.retries:
                await asyncio.sleep(0.4 * (2 ** attempt))
        raise ProviderResponseError(f"Groq request failed: {last_error}")
