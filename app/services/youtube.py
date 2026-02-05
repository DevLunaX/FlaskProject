"""Small helper to query (or stub) YouTube search results.

If no ``YOUTUBE_API_KEY`` is configured, the functions return a static
sample payload so local development and tests do not depend on the
external API.
"""

from __future__ import annotations

import requests

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# Minimal, locally served sample items to avoid external calls when the
# API key is missing or a request fails.
SAMPLE_VIDEOS = [
    {
        "id": "dQw4w9WgXcQ",
        "title": "Habitos saludables para el dia a dia",
        "channel": "Bienestar Hoy",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "publishedAt": "2023-05-01T12:00:00Z",
        "description": "Consejos rapidos para mejorar tu rutina de alimentacion.",
    },
    {
        "id": "kXYiU_JCYtU",
        "title": "Ejercicios rapidos en casa",
        "channel": "Move Fit",
        "url": "https://www.youtube.com/watch?v=kXYiU_JCYtU",
        "thumbnail": "https://i.ytimg.com/vi/kXYiU_JCYtU/hqdefault.jpg",
        "publishedAt": "2023-07-15T09:30:00Z",
        "description": "Rutina de 10 minutos para estudiantes ocupados.",
    },
    {
        "id": "3JZ_D3ELwOQ",
        "title": "Planifica tus comidas: guia facil",
        "channel": "NutriTips",
        "url": "https://www.youtube.com/watch?v=3JZ_D3ELwOQ",
        "thumbnail": "https://i.ytimg.com/vi/3JZ_D3ELwOQ/hqdefault.jpg",
        "publishedAt": "2023-03-22T18:45:00Z",
        "description": "Como armar menus semanales balanceados.",
    },
]


def search_videos(
    *,
    query: str,
    api_key: str | None,
    max_results: int = 6,
    related_to: str | None = None,
) -> dict:
    """Return video search results or a local sample when offline.

    Args:
        query: Text to search for.
        api_key: YouTube Data API key. When missing, returns sample data.
        max_results: Clamp between 1 and 15 to keep responses small.
        related_to: Optional video id to get recommendations related to that item.
    """

    max_results = max(1, min(max_results, 15))

    # Short-circuit when no API key is configured to avoid network calls during tests.
    if not api_key:
        return _build_sample_payload(query=query, related_to=related_to, max_results=max_results, reason="missing_api_key")

    params = {
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": max_results,
        "key": api_key,
    }

    if related_to:
        # relatedToVideoId requires a generic query, so keep a short one by default
        # but allow the caller's query to pass through for better matching.
        params["relatedToVideoId"] = related_to

    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:  # pragma: no cover - exercised indirectly
        return _build_sample_payload(
            query=query,
            related_to=related_to,
            max_results=max_results,
            reason=f"fallback:{exc.__class__.__name__}",
            error=str(exc),
        )

    items: list[dict] = []
    for item in data.get("items", []):
        normalized = _normalize_item(item)
        if normalized:
            items.append(normalized)

    return {
        "source": "youtube",
        "query": query,
        "relatedTo": related_to,
        "count": len(items),
        "items": items,
    }


def _normalize_item(item: dict | None) -> dict | None:
    if not item:
        return None

    snippet = item.get("snippet", {})
    video_id = (item.get("id") or {}).get("videoId")
    if not video_id:
        return None

    return {
        "id": video_id,
        "title": snippet.get("title", ""),
        "channel": snippet.get("channelTitle", ""),
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "thumbnail": (snippet.get("thumbnails", {}) or {}).get("high", {}).get("url")
        or (snippet.get("thumbnails", {}) or {}).get("default", {}).get("url"),
        "publishedAt": snippet.get("publishedAt"),
        "description": snippet.get("description", ""),
    }


def _build_sample_payload(*, query: str, related_to: str | None, max_results: int, reason: str, error: str | None = None) -> dict:
    items = SAMPLE_VIDEOS[:max_results]
    payload = {
        "source": "sample",
        "query": query,
        "relatedTo": related_to,
        "count": len(items),
        "items": items,
        "reason": reason,
    }
    if error:
        payload["error"] = error
    return payload
