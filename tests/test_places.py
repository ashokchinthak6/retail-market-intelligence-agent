"""Unit tests for Places response normalization."""

from app.tools.places import _normalize_place


def test_normalize_place_flattens_google_payload() -> None:
    payload = {
        "name": "places/example-id",
        "displayName": {"text": "Example Retailer"},
        "formattedAddress": "100 Main Street",
        "location": {"latitude": 35.2, "longitude": -80.8},
        "rating": 4.6,
        "userRatingCount": 325,
        "priceLevel": "PRICE_LEVEL_MODERATE",
        "types": ["clothing_store", "store"],
    }

    normalized = _normalize_place(payload)

    assert normalized["place_id"] == "places/example-id"
    assert normalized["name"] == "Example Retailer"
    assert normalized["rating_count"] == 325
    assert normalized["price_level"] == 2


def test_normalize_place_tolerates_sparse_payload() -> None:
    normalized = _normalize_place({})
    assert normalized["name"] == ""
    assert normalized["rating_count"] == 0
    assert normalized["types"] == []

