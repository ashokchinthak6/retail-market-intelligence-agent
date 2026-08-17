"""Typed request and scoring models."""

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """Normalized retail research request."""

    address: str = Field(min_length=5, max_length=300)
    retail_concept: str = Field(min_length=2, max_length=120)
    customer_segment: str | None = Field(default=None, max_length=200)
    radius_meters: int = Field(default=1600, ge=100, le=50_000)

    @field_validator("address", "retail_concept")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value cannot be blank")
        return value


class SiteScore(BaseModel):
    """Deterministic site-score components."""

    overall: float = Field(ge=0, le=100)
    competition: float = Field(ge=0, le=100)
    accessibility: float = Field(ge=0, le=100)
    demand: float = Field(ge=0, le=100)
    anchor_strength: float = Field(ge=0, le=100)

