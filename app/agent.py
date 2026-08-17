"""Root orchestrator for the Retail Market Intelligence Agent.

The orchestration pattern is adapted from Google ADK Samples' Market Research
Agent. Copyright 2026 Google LLC. Modifications Copyright 2026 Ashok
Chinthakindi. Licensed under the Apache License, Version 2.0.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from .agents import (
    competitor_agent,
    demand_agent,
    location_agent,
    whitespace_agent,
)
from .config import get_settings
from .prompts import ORCHESTRATOR_PROMPT
from .tools.places import geocode_address

root_agent = LlmAgent(
    name="retail_market_intelligence_orchestrator",
    model=get_settings().model_name,
    description=(
        "Coordinates a retail site-selection research workflow and produces "
        "an evidence-grounded expansion recommendation."
    ),
    instruction=ORCHESTRATOR_PROMPT,
    tools=[
        geocode_address,
        AgentTool(agent=competitor_agent),
        AgentTool(agent=location_agent),
        AgentTool(agent=demand_agent),
        AgentTool(agent=whitespace_agent),
    ],
)

