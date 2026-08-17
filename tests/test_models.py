"""Tests for validated input and output models."""

import pytest
from pydantic import ValidationError

from app.models import ResearchRequest, SiteScore


def test_research_request_strips_required_text() -> None:
    request = ResearchRequest(
        address="  4400 Sharon Road, Charlotte, NC  ",
        retail_concept="  off-price apparel  ",
    )
    assert request.address == "4400 Sharon Road, Charlotte, NC"
    assert request.retail_concept == "off-price apparel"


def test_research_request_rejects_invalid_radius() -> None:
    with pytest.raises(ValidationError):
        ResearchRequest(
            address="4400 Sharon Road, Charlotte, NC",
            retail_concept="apparel",
            radius_meters=99,
        )


def test_site_score_rejects_out_of_range_component() -> None:
    with pytest.raises(ValidationError):
        SiteScore(
            overall=80,
            competition=101,
            accessibility=75,
            demand=82,
            anchor_strength=70,
        )

