# Copyright 2026 Google LLC
# Modifications Copyright 2026 Ashok Chinthakindi
# Licensed under the Apache License, Version 2.0.

"""Google Places API v1 and Geocoding tools for ADK agents.

Adapted from Google ADK Samples' Market Research Agent. The implementation
adds centralized error normalization, configurable result limits, request
timeouts, and fields useful for retail analysis.
"""

import json
import os
from typing import Any

import httpx

from ..config import get_settings

_PLACES_BASE_URL = "https://places.googleapis.com/v1"
_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
_REQUEST_TIMEOUT_SECONDS = 20.0

_PRICE_LEVEL_MAP = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}


def _api_key() -> str:
    key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY environment variable is not set")
    return key


def _normalize_place(place: dict[str, Any]) -> dict[str, Any]:
    """Flatten a Places API v1 item into stable agent-friendly fields."""

    location = place.get("location") or {}
    display_name = place.get("displayName") or {}
    display_text = (
        display_name.get("text", "")
        if isinstance(display_name, dict)
        else str(display_name)
    )
    price_raw = place.get("priceLevel")
    return {
        "place_id": place.get("name") or place.get("id", ""),
        "name": display_text,
        "address": place.get("formattedAddress", ""),
        "lat": location.get("latitude"),
        "lng": location.get("longitude"),
        "rating": place.get("rating"),
        "rating_count": place.get("userRatingCount", 0),
        "price_level": _PRICE_LEVEL_MAP.get(price_raw) if price_raw else None,
        "types": place.get("types", []),
        "opening_hours": place.get("currentOpeningHours", {}),
        "website": place.get("websiteUri"),
        "google_maps_uri": place.get("googleMapsUri"),
    }


def _error_payload(error: Exception) -> str:
    """Return a safe JSON error without exposing credentials or headers."""

    if isinstance(error, httpx.HTTPStatusError):
        return json.dumps(
            {
                "error": "Google Maps Platform request failed",
                "status_code": error.response.status_code,
                "retryable": error.response.status_code
                in {408, 429, 500, 502, 503, 504},
            }
        )
    if isinstance(error, httpx.TimeoutException):
        return json.dumps(
            {
                "error": "Google Maps Platform request timed out",
                "retryable": True,
            }
        )
    return json.dumps({"error": str(error), "retryable": False})


async def geocode_address(address: str) -> str:
    """Convert a full address into coordinates and a formatted address."""

    try:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(
                _GEOCODING_URL,
                params={"address": address.strip(), "key": _api_key()},
            )
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, RuntimeError) as error:
        return _error_payload(error)

    if data.get("status") != "OK" or not data.get("results"):
        return json.dumps(
            {
                "error": "Address could not be geocoded",
                "status": data.get("status", "UNKNOWN"),
            }
        )

    result = data["results"][0]
    location = result["geometry"]["location"]
    return json.dumps(
        {
            "lat": location["lat"],
            "lng": location["lng"],
            "formatted_address": result["formatted_address"],
            "location_type": result["geometry"].get("location_type"),
        }
    )


async def nearby_search(
    lat: float,
    lng: float,
    business_type: str,
    radius_meters: int | None = None,
    max_results: int | None = None,
) -> str:
    """Find businesses or location anchors near a coordinate."""

    settings = get_settings()
    radius = radius_meters or settings.default_radius_meters
    result_limit = min(max_results or settings.max_place_results, 20)
    normalized_type = business_type.lower().replace(" ", "_").replace("-", "_")

    try:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{_PLACES_BASE_URL}/places:searchNearby",
                json={
                    "includedTypes": [normalized_type],
                    "maxResultCount": result_limit,
                    "locationRestriction": {
                        "circle": {
                            "center": {"latitude": lat, "longitude": lng},
                            "radius": float(min(max(radius, 100), 50_000)),
                        }
                    },
                },
                headers={
                    "X-Goog-Api-Key": _api_key(),
                    "X-Goog-FieldMask": (
                        "places.name,places.id,places.displayName,"
                        "places.formattedAddress,places.rating,"
                        "places.userRatingCount,places.priceLevel,"
                        "places.location,places.types,places.googleMapsUri"
                    ),
                },
            )
            response.raise_for_status()
            places = response.json().get("places", [])
    except (httpx.HTTPError, RuntimeError) as error:
        return _error_payload(error)

    return json.dumps([_normalize_place(place) for place in places])


async def text_search(
    query: str,
    lat: float,
    lng: float,
    radius_meters: int | None = None,
) -> str:
    """Run a free-text Places search biased toward a target coordinate."""

    radius = radius_meters or get_settings().default_radius_meters
    try:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{_PLACES_BASE_URL}/places:searchText",
                json={
                    "textQuery": query.strip(),
                    "locationBias": {
                        "circle": {
                            "center": {"latitude": lat, "longitude": lng},
                            "radius": float(min(max(radius, 100), 50_000)),
                        }
                    },
                    "maxResultCount": get_settings().max_place_results,
                },
                headers={
                    "X-Goog-Api-Key": _api_key(),
                    "X-Goog-FieldMask": (
                        "places.name,places.id,places.displayName,"
                        "places.formattedAddress,places.rating,"
                        "places.userRatingCount,places.priceLevel,"
                        "places.location,places.types,places.googleMapsUri"
                    ),
                },
            )
            response.raise_for_status()
            places = response.json().get("places", [])
    except (httpx.HTTPError, RuntimeError) as error:
        return _error_payload(error)

    return json.dumps([_normalize_place(place) for place in places])


async def place_details(place_id: str) -> str:
    """Get ratings, hours, website, and other details for one place."""

    resource = place_id if place_id.startswith("places/") else f"places/{place_id}"
    fields = (
        "name,id,displayName,formattedAddress,rating,userRatingCount,"
        "priceLevel,currentOpeningHours,types,location,websiteUri,googleMapsUri"
    )
    try:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{_PLACES_BASE_URL}/{resource}",
                headers={
                    "X-Goog-Api-Key": _api_key(),
                    "X-Goog-FieldMask": fields,
                },
            )
            response.raise_for_status()
            place = response.json()
    except (httpx.HTTPError, RuntimeError) as error:
        return _error_payload(error)

    return json.dumps(_normalize_place(place))
