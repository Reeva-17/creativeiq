
import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    """Extract JSON from a Gemini response."""

    if not text or not text.strip():
        raise ValueError("Gemini returned an empty response.")

    cleaned = text.strip()

    # Remove Markdown code fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Find JSON object or array inside surrounding text
    decoder = json.JSONDecoder()

    for index, character in enumerate(cleaned):
        if character in "[{":
            try:
                result, _ = decoder.raw_decode(cleaned[index:])
                return result
            except json.JSONDecodeError:
                continue

    raise ValueError("Could not extract valid JSON from Gemini response.")


def validate_exact_count(items: list, expected: int, name: str):
    if not isinstance(items, list):
        raise ValueError(f"{name} must be a list.")

    if len(items) != expected:
        raise ValueError(
            f"Expected {expected} {name}, received {len(items)}."
        )
