import pytest
import requests

from creative_generation.services.text_generator import TextGenerationError, generate_marketing_text


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text
        self.reason = "test response"

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._payload


def test_uses_configured_model_and_retries_timeout(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "configured-model")
    monkeypatch.setenv("GEMINI_MAX_RETRIES", "1")
    responses = [
        requests.Timeout(),
        FakeResponse(payload={"candidates": [{"content": {"parts": [{"text": "Campaign copy"}]}}]}),
    ]
    calls = []

    def post(url, **kwargs):
        calls.append(url)
        value = responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr("creative_generation.services.text_generator.requests.post", post)
    monkeypatch.setattr("creative_generation.services.text_generator.time.sleep", lambda _: None)
    assert generate_marketing_text("brief") == "Campaign copy"
    assert len(calls) == 2
    assert "/configured-model:" in calls[0]


def test_non_retryable_gemini_error_is_clear(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        "creative_generation.services.text_generator.requests.post",
        lambda *_, **__: FakeResponse(400, {"error": {"message": "bad request"}}),
    )
    with pytest.raises(TextGenerationError, match="bad request"):
        generate_marketing_text("brief")
