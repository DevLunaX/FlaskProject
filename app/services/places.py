"""Helpers to search nearby places (pharmacies, supplement shops, etc.).

Uses OpenStreetMap's Overpass API with a graceful local fallback so the
frontend can render sample data even without internet access.
"""

from __future__ import annotations

import math
from typing import Iterable

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

CATEGORY_QUERIES: dict[str, str] = {
    "pharmacy": 'node["amenity"="pharmacy"](around:{radius},{lat},{lon});',
    "supplements": 'node["shop"="nutrition_supplements"](around:{radius},{lat},{lon});',
    "health_food": 'node["shop"="health_food"](around:{radius},{lat},{lon});',
    "supermarket": 'node["shop"="supermarket"](around:{radius},{lat},{lon});',
}

SAMPLE_PLACES = [
    {
        "id": "sample-1",
        "name": "Farmacia Universidad",
        "type": "pharmacy",
        "address": "Av. Principal 123",
        "lat": 19.4326,
        "lon": -99.1332,
        "distance_km": 0.25,
    },
    {
        "id": "sample-2",
        "name": "VitaFit Suplementos",
        "type": "supplements",
        "address": "Calle Salud 45",
        "lat": 19.4312,
        "lon": -99.1288,
        "distance_km": 0.6,
    },
    {
        "id": "sample-3",
        "name": "Mercado Natural",
        "type": "health_food",
        "address": "Plaza Central, Local 12",
        "lat": 19.4301,
        "lon": -99.1355,
        "distance_km": 1.1,
    },
]


def search_places(
    *,
    lat: float,
    lon: float,
    radius_m: int = 3000,
    categories: Iterable[str] | None = None,
    limit: int = 20,
) -> dict:
    """Fetch nearby places or return a static sample if offline."""

    radius_m = max(500, min(int(radius_m), 10000))
    categories = [c for c in (categories or ["pharmacy", "supplements"]) if c in CATEGORY_QUERIES]
    if not categories:
        categories = ["pharmacy"]

    query_blocks = [CATEGORY_QUERIES[c].format(radius=radius_m, lat=lat, lon=lon) for c in categories]
    query = f"""
    [out:json][timeout:15];
    (
        {' '.join(query_blocks)}
    );
    out center {limit};
    """

    try:
        response = requests.post(OVERPASS_URL, data=query.encode("utf-8"), timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:  # pragma: no cover - network dependent
        return _build_sample(lat=lat, lon=lon, reason=f"fallback:{exc.__class__.__name__}", error=str(exc), limit=limit)

    places: list[dict] = []
    for element in data.get("elements", []):
        tags = element.get("tags", {}) or {}
        place_lat = element.get("lat")
        place_lon = element.get("lon")
        if place_lat is None or place_lon is None:
            continue

        place_type = _resolve_type(tags)
        name = tags.get("name") or tags.get("brand") or "Ubicacion sin nombre"
        address = _format_address(tags)
        distance = _haversine_km(lat, lon, place_lat, place_lon)

        places.append(
            {
                "id": element.get("id"),
                "name": name,
                "type": place_type,
                "address": address,
                "lat": place_lat,
                "lon": place_lon,
                "distance_km": round(distance, 2),
            }
        )

    places.sort(key=lambda p: p.get("distance_km", 0))
    places = places[:limit]

    return {
        "source": "overpass",
        "count": len(places),
        "items": places,
        "center": {"lat": lat, "lon": lon, "radius_m": radius_m},
    }


def _resolve_type(tags: dict) -> str:
    if "amenity" in tags and tags.get("amenity") == "pharmacy":
        return "pharmacy"
    if tags.get("shop") == "nutrition_supplements":
        return "supplements"
    if tags.get("shop") == "health_food":
        return "health_food"
    if tags.get("shop") == "supermarket":
        return "supermarket"
    return tags.get("shop") or tags.get("amenity") or "poi"


def _format_address(tags: dict) -> str:
    parts = [
        tags.get("addr:street"),
        tags.get("addr:housenumber"),
        tags.get("addr:city"),
    ]
    return ", ".join([p for p in parts if p])


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _build_sample(*, lat: float, lon: float, reason: str, error: str | None, limit: int) -> dict:
    items = SAMPLE_PLACES[:limit]
    return {
        "source": "sample",
        "count": len(items),
        "items": items,
        "center": {"lat": lat, "lon": lon},
        "reason": reason,
        "error": error,
    }
