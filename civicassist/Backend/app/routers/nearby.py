from math import atan2, cos, radians, sin, sqrt
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter(prefix="/api/nearby", tags=["Nearby Services"])

# Mapbox Search Box is used for POI search. Text queries are deliberately
# specific so that a search for lawyers does not return unrelated services.
SEARCH_QUERIES = {
    "lawyers": ["lawyer advocate law office legal services"],
    "government": ["government office collectorate municipal corporation taluk office revenue office"],
    "service_centers": ["government service centre common service centre CSC e-seva eSeva"],
    "legal_aid": ["legal aid centre legal services authority DLSA TLSC"],
    "police": ["police station"],
    "courthouse": ["court courthouse district court high court magistrate court"],
}

class NearbySearchRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category: str = Field("lawyers")
    radius: int = Field(5000, ge=500, le=25000)


def distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius = 6371000.0
    p1, p2 = radians(lat1), radians(lat2)
    dp = radians(lat2 - lat1)
    dl = radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return earth_radius * 2 * atan2(sqrt(a), sqrt(max(0.0, 1 - a)))


def make_place(feature: Dict[str, Any], request: NearbySearchRequest) -> Dict[str, Any] | None:
    props = feature.get("properties") or {}
    coords = props.get("coordinates") or feature.get("geometry", {}).get("coordinates") or {}

    if isinstance(coords, dict):
        lon = coords.get("longitude")
        lat = coords.get("latitude")
    elif isinstance(coords, list) and len(coords) >= 2:
        lon, lat = coords[0], coords[1]
    else:
        return None

    if lat is None or lon is None:
        return None

    lat, lon = float(lat), float(lon)
    distance = distance_meters(request.latitude, request.longitude, lat, lon)
    if distance > request.radius:
        return None

    name = props.get("name") or props.get("name_preferred") or "Unnamed place"
    address = (
        props.get("full_address")
        or props.get("place_formatted")
        or props.get("address")
        or "Address unavailable"
    )

    context = props.get("context") or {}
    phone = props.get("phone")
    website = props.get("website")

    return {
        "id": props.get("mapbox_id") or f"place:{lat}:{lon}:{name}",
        "name": str(name),
        "address": str(address),
        "latitude": lat,
        "longitude": lon,
        "phone": phone,
        "website": website,
        "open_now": None,
        "business_status": None,
        "categories": [props.get("poi_category") or props.get("maki") or "poi"],
        "distance": round(distance, 1),
        "maps_url": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}",
        "mapbox_id": props.get("mapbox_id"),
        "context": context,
    }


async def mapbox_search(request: NearbySearchRequest, query: str) -> List[Dict[str, Any]]:
    if not settings.MAPBOX_ACCESS_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="MAPBOX_ACCESS_TOKEN is missing. Add it to Backend/.env and restart the backend.",
        )

    url = "https://api.mapbox.com/search/searchbox/v1/forward"
    params = {
        "q": query,
        "proximity": f"{request.longitude},{request.latitude}",
        "limit": 10,
        "language": "en",
        "country": "IN",
        "types": "poi",
        "access_token": settings.MAPBOX_ACCESS_TOKEN,
    }

    headers = {"User-Agent": "CivicAssistAI/1.0 (college project)"}
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), follow_redirects=True) as client:
        response = await client.get(url, params=params, headers=headers)

    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text[:500]
        raise RuntimeError(f"Mapbox Search API HTTP {response.status_code}: {detail}")

    data = response.json()
    places: List[Dict[str, Any]] = []
    for feature in data.get("features", []):
        place = make_place(feature, request)
        if place:
            places.append(place)
    return places


@router.get("/config")
async def nearby_config() -> Dict[str, Any]:
    # Mapbox public access tokens are intended to be used by browser map SDKs.
    # Search requests themselves remain proxied through the backend.
    return {
        "provider": "mapbox",
        "places_provider": "Mapbox Search Box API",
        "requires_api_key": True,
        "mapbox_access_token": settings.MAPBOX_ACCESS_TOKEN,
    }


@router.post("/search")
async def search_nearby(request: NearbySearchRequest) -> Dict[str, Any]:
    category = request.category.strip().lower()
    queries = SEARCH_QUERIES.get(category)
    if not queries:
        raise HTTPException(status_code=400, detail="Unsupported nearby-service category.")

    all_places: List[Dict[str, Any]] = []
    seen = set()
    errors = []

    for query in queries:
        try:
            results = await mapbox_search(request, query)
            for place in results:
                key = place.get("mapbox_id") or f"{round(place['latitude'], 5)}:{round(place['longitude'], 5)}:{place['name'].lower()}"
                if key not in seen:
                    seen.add(key)
                    all_places.append(place)
        except HTTPException:
            raise
        except Exception as exc:
            errors.append(str(exc))

    all_places.sort(key=lambda p: p["distance"])
    all_places = all_places[:30]

    if not all_places and errors:
        raise HTTPException(status_code=502, detail=errors[-1])

    return {
        "category": category,
        "center": {"latitude": request.latitude, "longitude": request.longitude},
        "radius": request.radius,
        "count": len(all_places),
        "places": all_places,
        "provider": "Mapbox Search Box + Mapbox Maps",
    }
