from pydantic import BaseModel, Field, HttpUrl, field_validator


class SocialLink(BaseModel):
    platform: str = Field(min_length=1, max_length=60)
    url: HttpUrl


class BrandInput(BaseModel):
    """Information supplied by the user; only name and industry are required."""
    brand_name: str = Field(min_length=1, max_length=120)
    industry: str = Field(min_length=1, max_length=120)
    website_url: HttpUrl | None = None
    business_description: str | None = Field(default=None, max_length=4000)
    products_services: list[str] = Field(default_factory=list, max_length=30)
    target_audience: str | None = Field(default=None, max_length=1000)
    positioning: str | None = Field(default=None, max_length=1000)
    brand_values: list[str] = Field(default_factory=list, max_length=20)
    social_media_links: list[SocialLink] = Field(default_factory=list, max_length=12)
    additional_information: str | None = Field(default=None, max_length=4000)

    @field_validator("products_services", "brand_values")
    @classmethod
    def no_blank_items(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("items cannot be blank")
        return value


class CompetitorRequest(BaseModel):
    brand: BrandInput
    competitor_names: list[str] = Field(default_factory=list, max_length=15)
    research_urls: list[HttpUrl] = Field(default_factory=list, max_length=30)
