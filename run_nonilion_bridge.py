"""Run CreativeIQ as a live Nonilion room agent.

Start the FastAPI backend first, then run this script in a second terminal.
Only messages addressed to @CreativeIQ trigger the campaign workflow.
"""
from __future__ import annotations

import json
import os
import re
import time
from typing import Any

import httpx
from dotenv import load_dotenv

from app.services.nonilion_mcp import NonilionMCPClient, NonilionMCPError

load_dotenv()

AGENT_MENTION = "@creativeiq"
BASE_URL = os.getenv("CREATIVEIQ_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _events(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract the JSON event envelope from Nonilion's text content block."""
    for block in result.get("content", []):
        if block.get("type") != "text":
            continue
        text = block.get("text", "")
        start = text.find("{")
        if start < 0:
            continue
        try:
            envelope = json.loads(text[start:])
        except json.JSONDecodeError:
            continue
        events = envelope.get("events", [])
        return events if isinstance(events, list) else []
    return []


def _prompt_from_event(event: dict[str, Any]) -> str | None:
    if event.get("type") != "message":
        return None
    text = str(event.get("text", "")).strip()
    if AGENT_MENTION not in text.lower():
        return None
    prompt = re.sub(r"@creativeiq\b[,:\s]*", "", text, flags=re.IGNORECASE).strip()
    return prompt if len(prompt) >= 20 else None


def _run_campaign(prompt: str) -> dict[str, Any]:
    # Render/free-network connections can be reset while a long-running model
    # workflow is in progress. Retry only transport failures; HTTP responses
    # contain useful agent/provider errors and must be surfaced unchanged.
    last_transport_error: httpx.HTTPError | None = None
    for attempt in range(3):
        try:
            response = httpx.post(
                f"{BASE_URL}/api/v1/workflow/run-from-prompt",
                json={"prompt": prompt, "generate_poster": True, "max_revisions": 1},
                timeout=300,
            )
        except httpx.HTTPError as exc:
            last_transport_error = exc
            if attempt < 2:
                delay = 3 * (attempt + 1)
                print(f"Render connection interrupted ({exc}); retrying in {delay}s.")
                time.sleep(delay)
                continue
            raise RuntimeError(
                "Could not keep a connection to the hosted CreativeIQ service after 3 attempts: "
                f"{exc}"
            ) from exc

        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise RuntimeError(str(detail))
        return response.json()

    raise RuntimeError(f"Could not reach the hosted CreativeIQ service: {last_transport_error}")


def _summary(campaign: dict[str, Any]) -> str:
    handoff = campaign["campaign_handoff"]
    strategy = handoff["campaign_strategy"]
    evaluation = campaign["evaluations"][-1] if campaign.get("evaluations") else {}
    asset = campaign["creative_assets"][-1] if campaign.get("creative_assets") else {}
    lines = [
        f"Campaign complete: {strategy['campaign_name']}",
        f"Tagline: {strategy['main_tagline']}",
        f"Concept: {handoff['selected_concept_id']}",
        f"Final evaluation: {evaluation.get('overall_score', 'n/a')}/100 ({campaign['final_status']})",
    ]
    if asset.get("poster_url"):
        lines.append(f"Poster: {BASE_URL}{asset['poster_url']}")
    elif asset.get("image_url"):
        lines.append(f"Visual: {BASE_URL}{asset['image_url']}")
    lines.append("I can refine the campaign if you send another request.")
    return "\n".join(lines)


def main() -> None:
    client = NonilionMCPClient()
    print(f"CreativeIQ bridge is listening through Nonilion. Backend: {BASE_URL}")
    while True:
        try:
            for event in _events(client.listen(wait_seconds=25)):
                prompt = _prompt_from_event(event)
                if not prompt:
                    continue
                client.reply("I am building your four-agent campaign now. This can take a few minutes.", speak=True)
                try:
                    campaign = _run_campaign(prompt)
                    client.reply(_summary(campaign), speak=False)
                except Exception as exc:
                    client.reply(f"I could not complete the campaign: {exc}", speak=False)
        except NonilionMCPError as exc:
            print(f"Nonilion connection error: {exc}. Retrying in 5 seconds.")
            time.sleep(5)


if __name__ == "__main__":
    main()
