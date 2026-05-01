import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
KINOPOISK_API_KEY = os.getenv("KINOPOISK_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
KINOPOISK_BASE_URL = "https://api.kinopoisk.dev/v1.4"

DB_PATH = "movies.db"
