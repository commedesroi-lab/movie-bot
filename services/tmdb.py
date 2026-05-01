import httpx
from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE

GENRE_MAP = {
    28: "боевик", 12: "приключения", 16: "мультфильм", 35: "комедия",
    80: "криминал", 99: "документальный", 18: "драма", 10751: "семейный",
    14: "фэнтези", 36: "история", 27: "ужасы", 10402: "музыка",
    9648: "детектив", 10749: "мелодрама", 878: "фантастика",
    10770: "телефильм", 53: "триллер", 10752: "военный", 37: "вестерн",
}


async def search_movies(query: str) -> list[dict]:
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "ru-RU",
        "page": 1,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    results = []
    for movie in data.get("results", [])[:5]:
        year = movie.get("release_date", "")[:4] or "?"
        genres = ", ".join(
            GENRE_MAP.get(gid, "") for gid in movie.get("genre_ids", []) if GENRE_MAP.get(gid)
        )
        poster = (TMDB_IMAGE_BASE + movie["poster_path"]) if movie.get("poster_path") else None
        results.append({
            "tmdb_id": movie["id"],
            "title": movie.get("title", ""),
            "year": int(year) if year.isdigit() else None,
            "genres": genres,
            "overview": movie.get("overview", ""),
            "poster_url": poster,
        })
    return results


async def get_recommendations(tmdb_id: int) -> list[dict]:
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}/recommendations"
    params = {"api_key": TMDB_API_KEY, "language": "ru-RU", "page": 1}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        data = response.json()

    results = []
    for movie in data.get("results", [])[:10]:
        year = movie.get("release_date", "")[:4] or "?"
        genres = ", ".join(
            GENRE_MAP.get(gid, "") for gid in movie.get("genre_ids", []) if GENRE_MAP.get(gid)
        )
        poster = (TMDB_IMAGE_BASE + movie["poster_path"]) if movie.get("poster_path") else None
        results.append({
            "tmdb_id": movie["id"],
            "title": movie.get("title", ""),
            "year": int(year) if year.isdigit() else None,
            "genres": genres,
            "overview": (movie.get("overview") or "")[:300],
            "poster_url": poster,
        })
    return results


async def discover_by_genres(genre_names: list[str]) -> list[dict]:
    genre_ids = [str(k) for k, v in GENRE_MAP.items() if v in genre_names]
    if not genre_ids:
        return []

    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "ru-RU",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 500,
        "with_genres": "|".join(genre_ids[:3]),
        "page": 1,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        data = response.json()

    results = []
    for movie in data.get("results", [])[:15]:
        year = movie.get("release_date", "")[:4] or "?"
        genres = ", ".join(
            GENRE_MAP.get(gid, "") for gid in movie.get("genre_ids", []) if GENRE_MAP.get(gid)
        )
        poster = (TMDB_IMAGE_BASE + movie["poster_path"]) if movie.get("poster_path") else None
        results.append({
            "tmdb_id": movie["id"],
            "title": movie.get("title", ""),
            "year": int(year) if year.isdigit() else None,
            "genres": genres,
            "overview": (movie.get("overview") or "")[:300],
            "poster_url": poster,
        })
    return results
