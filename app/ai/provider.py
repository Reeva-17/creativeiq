from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def generate_json(self, prompt: str) -> dict[str, Any]:
        """Return a decoded JSON object or raise a provider exception."""
