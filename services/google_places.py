import requests
import streamlit as st


def get_api_key() -> str:
    """Get Google Places API key from Streamlit secrets or environment."""
    try:
        return st.secrets["GOOGLE_PLACES_API_KEY"]
    except (KeyError, FileNotFoundError):
        import os
        return os.environ.get("GOOGLE_PLACES_API_KEY", "")


def has_api_key() -> bool:
    """Check if a Google Places API key is configured."""
    return bool(get_api_key())


def search_places(query: str) -> list[dict]:
    """Search for places using Google Places API (New).

    Returns a list of dicts with: place_id, name, address, rating, total_reviews.
    """
    api_key = get_api_key()
    if not api_key:
        return []

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount",
    }
    body = {"textQuery": query}

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    results = []
    for place in data.get("places", []):
        results.append({
            "place_id": place.get("id", ""),
            "name": place.get("displayName", {}).get("text", ""),
            "address": place.get("formattedAddress", ""),
            "rating": place.get("rating", 0.0),
            "total_reviews": place.get("userRatingCount", 0),
        })
    return results


def get_place_details(place_id: str) -> dict | None:
    """Fetch place details including reviews.

    Note: The Places API returns at most 5 individual reviews, so this
    cannot provide a full star distribution. It returns:
    - rating (average)
    - total_reviews (count)
    - reviews (list of up to 5 reviews with star ratings)
    """
    api_key = get_api_key()
    if not api_key:
        return None

    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "id,displayName,formattedAddress,rating,userRatingCount,reviews",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    return {
        "place_id": data.get("id", ""),
        "name": data.get("displayName", {}).get("text", ""),
        "address": data.get("formattedAddress", ""),
        "rating": data.get("rating", 0.0),
        "total_reviews": data.get("userRatingCount", 0),
        "reviews": data.get("reviews", []),
    }
