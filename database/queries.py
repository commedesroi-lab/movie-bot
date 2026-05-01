from __future__ import annotations
import aiosqlite
from config import DB_PATH


async def add_movie(title: str, year: int, tmdb_id: int, kp_id: str,
                    genres: str, kp_rating: float, poster_url: str,
                    watched: int = 0) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM movies WHERE tmdb_id = ?", (tmdb_id,)
        )
        existing = await cursor.fetchone()
        if existing:
            return False  # фильм уже в списке

        await db.execute(
            """INSERT INTO movies (title, year, tmdb_id, kp_id, genres, kp_rating, poster_url, watched)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, year, tmdb_id, kp_id, genres, kp_rating, poster_url, watched)
        )
        await db.commit()
        return True


async def get_all_movies(watched: int | None = None) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if watched is None:
            cursor = await db.execute(
                "SELECT * FROM movies ORDER BY watched ASC, added_at DESC"
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM movies WHERE watched = ? ORDER BY added_at DESC",
                (watched,)
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def mark_as_watched(movie_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE movies SET watched = 1 WHERE id = ?", (movie_id,)
        )
        await db.commit()


async def get_watched_genres() -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT genres FROM movies WHERE watched = 1 AND genres IS NOT NULL"
        )
        rows = await cursor.fetchall()

    genre_counts: dict[str, int] = {}
    for row in rows:
        for genre in row[0].split(","):
            g = genre.strip()
            if g:
                genre_counts[g] = genre_counts.get(g, 0) + 1

    sorted_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)
    return sorted_genres[:5]


async def get_all_tmdb_ids() -> set[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT tmdb_id FROM movies WHERE tmdb_id IS NOT NULL")
        rows = await cursor.fetchall()
    return {row[0] for row in rows}
