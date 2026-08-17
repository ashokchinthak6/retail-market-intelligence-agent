"""Environment-backed application configuration."""

import os
from functools import lru_cache

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime settings shared by agents and tools."""

    model_name: str = Field(default="gemini-3.5-flash")
    default_radius_meters: int = Field(default=1600, ge=100, le=50_000)
    max_place_results: int = Field(default=20, ge=1, le=20)


@lru_cache
def get_settings() -> Settings:
    """Load and validate non-secret configuration once."""

    return Settings(
        model_name=os.getenv("MODEL_NAME", "gemini-3.5-flash"),
        default_radius_meters=int(os.getenv("DEFAULT_RADIUS_METERS", "1600")),
        max_place_results=int(os.getenv("MAX_PLACE_RESULTS", "20")),
    )
