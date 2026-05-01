from __future__ import annotations
import httpx
from config import KINOPOISK_API_KEY, KINOPOISK_BASE_URL


async def get_kp_rating(title: str, year: int | None) -> tuple[str | None, float | None]:
    """Возвращает (kp_id, kp_rating) или (None, None) если не найдено."""
    url = f"{KINOPOISK_BASE_URL}/movie/search"
    params = {"query": title, "limit": 5, "page": 1}
    headers = {"X-API-KEY": KINOPOISK_API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                return None, None
            data = response.json()
    except Exception:
        return None, None

    movies = data.get("docs", [])
    if not movies:
        return None, None

    best = None
    for movie in movies:
        movie_year = movie.get("year")
        if year and movie_year and abs(movie_year - year) <= 1:
            best = movie
            break

    if not best:
        best = movies[0]

    kp_id = str(best.get("id", ""))
    rating = best.get("rating", {}).get("kp")
    return kp_id, rating
