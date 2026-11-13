import json
from types import SimpleNamespace
import pytest

from app.ai.groq_provider import GroqProvider
from app.core.exceptions import ProviderResponseError, ProviderUnavailableError


def completion(content: str):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class FakeCompletions:
    def __init__(self, responses): self.responses, self.calls = list(responses), 0
    async def create(self, **kwargs):
        self.calls += 1
        value = self.responses.pop(0)
        if isinstance(value, Exception): raise value
        return completion(value)


class FakeClient:
    def __init__(self, responses): self.completions = FakeCompletions(responses); self.chat = SimpleNamespace(completions=self.completions)


@pytest.mark.asyncio
async def test_successful_groq_response_is_decoded():
    client = FakeClient([json.dumps({"brand_dna": {}, "visual_identity": {}})])
    result = await GroqProvider("test-key", "test-model", client=client).generate_json("input")
    assert result["brand_dna"] == {}
    assert client.completions.calls == 1


@pytest.mark.asyncio
async def test_malformed_groq_json_raises_provider_error():
    client = FakeClient(["not json"])
    with pytest.raises(ProviderResponseError, match="Groq request failed"):
        await GroqProvider("test-key", "test-model", retries=0, client=client).generate_json("input")


@pytest.mark.asyncio
async def test_groq_api_error_is_retried_and_reported():
    client = FakeClient([RuntimeError("API unavailable"), RuntimeError("API unavailable")])
    with pytest.raises(ProviderResponseError):
        await GroqProvider("test-key", "test-model", retries=1, client=client).generate_json("input")
    assert client.completions.calls == 2


@pytest.mark.asyncio
async def test_groq_timeout_is_retried_and_reported():
    client = FakeClient([TimeoutError("timeout"), TimeoutError("timeout")])
    with pytest.raises(ProviderResponseError):
        await GroqProvider("test-key", "test-model", retries=1, client=client).generate_json("input")
    assert client.completions.calls == 2


@pytest.mark.asyncio
async def test_missing_groq_key_never_calls_client():
    with pytest.raises(ProviderUnavailableError, match="GROQ_API_KEY"):
        await GroqProvider(None, "test-model").generate_json("input")
