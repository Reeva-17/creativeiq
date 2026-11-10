import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Groq Settings
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-120b", validation_alias="GROQ_MODEL")
    groq_timeout_seconds: float = Field(default=30.0, validation_alias="GROQ_TIMEOUT_SECONDS")
    groq_max_retries: int = Field(default=2, validation_alias="GROQ_MAX_RETRIES")

    # Gemini Settings (Fallback / Alternative Provider)
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.6-flash", validation_alias="GEMINI_MODEL")

    # Tavily Web Search (Optional for Person 1)
    tavily_api_key: str | None = Field(default=None, validation_alias="TAVILY_API_KEY")

    # Paths
    project_root: Path = PROJECT_ROOT
    output_dir: Path = PROJECT_ROOT / "outputs"

    # Evaluation Weights (Must sum to 100)
    evaluation_weights: dict[str, float] = {
        "creativity": 25.0,
        "audience_relevance": 25.0,
        "brand_consistency": 25.0,
        "campaign_objectives_alignment": 25.0,
    }


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
