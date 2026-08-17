"""Specialist Google ADK agents.

The multi-agent structure is adapted from Google ADK Samples' Market Research
Agent. Copyright 2026 Google LLC. Modifications Copyright 2026 Ashok
Chinthakindi. Licensed under the Apache License, Version 2.0.
"""

from google.adk.agents import LlmAgent

from .config import get_settings
from .prompts import (
    COMPETITOR_PROMPT,
    DEMAND_PROMPT,
    LOCATION_PROMPT,
    WHITESPACE_PROMPT,
)
from .tools.places import nearby_search, place_details, text_search
from .tools.scoring import score_competitor, score_location

_MODEL = get_settings().model_name

competitor_agent = LlmAgent(
    name="competitor_intelligence_agent",
    model=_MODEL,
    description=(
        "Finds direct and adjacent retail competitors, measures saturation, "
        "and ranks competitive pressure with deterministic scoring."
    ),
    instruction=COMPETITOR_PROMPT,
    tools=[nearby_search, text_search, place_details, score_competitor],
)

location_agent = LlmAgent(
    name="location_viability_agent",
    model=_MODEL,
    description=(
        "Scores a proposed retail site using accessibility, competition, "
        "demand, and nearby anchor evidence."
    ),
    instruction=LOCATION_PROMPT,
    tools=[nearby_search, text_search, score_location],
)

demand_agent = LlmAgent(
    name="demand_signals_agent",
    model=_MODEL,
    description=(
        "Evaluates category activity, review volume, operating patterns, and "
        "destination anchors as transparent demand and traffic proxies."
    ),
    instruction=DEMAND_PROMPT,
    tools=[nearby_search, text_search, place_details],
)

whitespace_agent = LlmAgent(
    name="retail_whitespace_agent",
    model=_MODEL,
    description=(
        "Identifies underserved concepts, assortments, services, and price "
        "positions around a proposed retail site."
    ),
    instruction=WHITESPACE_PROMPT,
    tools=[nearby_search, text_search, place_details],
)

