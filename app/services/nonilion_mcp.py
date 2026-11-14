"""Small authenticated client for CreativeIQ's Nonilion MCP connection.

The token is read only from the local environment.  It is never returned in
errors, responses, or logs.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv


class NonilionMCPError(RuntimeError):
    """A safe, user-actionable Nonilion MCP failure."""


class NonilionMCPClient:
    def __init__(self, endpoint: str | None = None, token: str | None = None) -> None:
        load_dotenv()
        self.endpoint = endpoint or os.getenv("NONILION_MCP_URL", "https://www.nonilion.com/mcp")
        self.token = token or os.getenv("NONILION_MCP_TOKEN")
        if not self.token:
            raise NonilionMCPError("NONILION_MCP_TOKEN is missing from .env")

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call one official Nonilion MCP tool via Streamable HTTP JSON-RPC."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        }
        try:
            # `listen` is a documented long-poll (up to 25 seconds).  Its
            # HTTP read timeout must leave enough room for network latency and
            # the server response, otherwise an idle room looks like a failed
            # MCP connection.
            wait_seconds = int((arguments or {}).get("wait_seconds", 0))
            timeout = httpx.Timeout(
                connect=15.0,
                read=max(45.0, wait_seconds + 30.0),
                write=15.0,
                pool=15.0,
            )
            response = httpx.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout,
            )
        except httpx.HTTPError as exc:
            raise NonilionMCPError(f"Could not reach Nonilion MCP: {exc}") from exc

        if response.status_code >= 400:
            raise NonilionMCPError(
                f"Nonilion MCP returned HTTP {response.status_code}: {response.text[:500]}"
            )
        try:
            data = response.json()
        except ValueError as exc:
            raise NonilionMCPError("Nonilion MCP returned invalid JSON") from exc

        if data.get("error"):
            raise NonilionMCPError(f"Nonilion MCP tool '{name}' failed: {data['error']}")
        result = data.get("result")
        if not isinstance(result, dict) or result.get("isError"):
            raise NonilionMCPError(f"Nonilion MCP tool '{name}' failed: {result}")
        return result

    def enter_room(self, room: str, name: str = "CreativeIQ") -> dict[str, Any]:
        return self.call_tool("enter_room", {"room": room, "name": name})

    def listen(self, wait_seconds: int = 20) -> dict[str, Any]:
        return self.call_tool("listen", {"wait_seconds": max(0, min(wait_seconds, 25))})

    def reply(self, text: str, speak: bool = False) -> dict[str, Any]:
        return self.call_tool("reply", {"text": text, "speak": speak})

    def say_out_loud(self, text: str) -> dict[str, Any]:
        return self.call_tool("say_out_loud", {"text": text})
