import aiosqlite
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                year        INTEGER,
                tmdb_id     INTEGER,
                kp_id       TEXT,
                genres      TEXT,
                kp_rating   REAL,
                poster_url  TEXT,
                watched     INTEGER DEFAULT 0,
                added_at    TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.commit()
