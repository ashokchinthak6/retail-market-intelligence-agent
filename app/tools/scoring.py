"""Deterministic retail scoring utilities.

LLMs gather and explain evidence; these functions keep the numerical logic
repeatable and directly testable.
"""

from math import asin, cos, radians, sin, sqrt


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Constrain a numeric value to an inclusive range."""

    return max(minimum, min(maximum, value))


def haversine_distance_meters(
    lat1: float, lng1: float, lat2: float, lng2: float
) -> float:
    """Return the great-circle distance between two coordinates."""

    earth_radius_meters = 6_371_000
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(delta_lng / 2) ** 2
    )
    return 2 * earth_radius_meters * asin(sqrt(a))


def calculate_competitive_score(
    rating: float | None,
    rating_count: int,
    price_level: int | None,
    distance_meters: float,
    radius_meters: float,
    target_price_level: int = 2,
) -> float:
    """Calculate competitive pressure on a 0-100 scale.

    Weighting: rating 35%, popularity 30%, distance 20%, price-position match
    15%. A larger value represents a stronger competitor.
    """

    safe_rating = clamp(float(rating or 0), 0, 5)
    rating_component = safe_rating / 5 * 35
    popularity_component = min(max(rating_count, 0) / 750, 1) * 30

    safe_radius = max(radius_meters, 1)
    distance_ratio = clamp(distance_meters / safe_radius, 0, 1)
    proximity_component = (1 - distance_ratio) * 20

    if price_level is None:
        price_component = 7.5
    else:
        price_difference = min(abs(price_level - target_price_level), 4)
        price_component = (1 - price_difference / 4) * 15

    return round(
        clamp(
            rating_component
            + popularity_component
            + proximity_component
            + price_component
        ),
        1,
    )


def score_competitor(
    rating: float | None,
    rating_count: int,
    price_level: int | None,
    distance_meters: float,
    radius_meters: float,
    target_price_level: int = 2,
) -> dict[str, float]:
    """ADK tool wrapper for deterministic competitor scoring."""

    return {
        "competitive_score": calculate_competitive_score(
            rating,
            rating_count,
            price_level,
            distance_meters,
            radius_meters,
            target_price_level,
        )
    }


def calculate_location_score(
    competition: float,
    accessibility: float,
    demand: float,
    anchor_strength: float,
) -> float:
    """Calculate a weighted retail site score on a 0-100 scale."""

    overall = (
        clamp(competition) * 0.25
        + clamp(accessibility) * 0.25
        + clamp(demand) * 0.30
        + clamp(anchor_strength) * 0.20
    )
    return round(clamp(overall), 1)


def score_location(
    competition: float,
    accessibility: float,
    demand: float,
    anchor_strength: float,
) -> dict[str, float]:
    """ADK tool wrapper returning components and overall score."""

    return {
        "overall": calculate_location_score(
            competition, accessibility, demand, anchor_strength
        ),
        "competition": clamp(competition),
        "accessibility": clamp(accessibility),
        "demand": clamp(demand),
        "anchor_strength": clamp(anchor_strength),
    }

