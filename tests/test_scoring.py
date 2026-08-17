"""Unit tests for deterministic retail scoring."""

from app.tools.scoring import (
    calculate_competitive_score,
    calculate_location_score,
    haversine_distance_meters,
    score_location,
)


def test_haversine_distance_same_point_is_zero() -> None:
    assert haversine_distance_meters(35.2271, -80.8431, 35.2271, -80.8431) == 0


def test_haversine_distance_is_symmetric() -> None:
    first = haversine_distance_meters(35.2271, -80.8431, 35.2260, -80.8400)
    second = haversine_distance_meters(35.2260, -80.8400, 35.2271, -80.8431)
    assert round(first, 6) == round(second, 6)


def test_competitive_score_rewards_strength_and_proximity() -> None:
    strong_nearby = calculate_competitive_score(4.8, 900, 2, 100, 1600)
    weak_distant = calculate_competitive_score(3.2, 40, 4, 1400, 1600)
    assert strong_nearby > weak_distant
    assert 0 <= weak_distant <= strong_nearby <= 100


def test_competitive_score_handles_missing_values() -> None:
    score = calculate_competitive_score(None, 0, None, 500, 1600)
    assert 0 <= score <= 100


def test_location_score_uses_documented_weights() -> None:
    score = calculate_location_score(80, 70, 90, 60)
    assert score == 76.5


def test_location_tool_clamps_components() -> None:
    result = score_location(120, -10, 80, 70)
    assert result["competition"] == 100
    assert result["accessibility"] == 0
    assert result["overall"] == 63.0

