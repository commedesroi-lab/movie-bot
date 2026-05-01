import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database.queries import get_all_movies, get_watched_genres, get_all_tmdb_ids, add_movie
from services.tmdb import get_recommendations, discover_by_genres
from services.kinopoisk import get_kp_rating


async def show_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Подбираю рекомендации на основе твоих просмотров...")

    watched = await get_all_movies(watched=1)
    if not watched:
        await update.message.reply_text(
            "Ты ещё ничего не посмотрел из списка 😊\n"
            "Отметь хотя бы один фильм как просмотренный — тогда смогу подобрать рекомендации!"
        )
        return

    existing_ids = await get_all_tmdb_ids()
    candidates: list[dict] = []

    random.shuffle(watched)
    for movie in watched[:5]:
        if movie.get("tmdb_id"):
            recs = await get_recommendations(movie["tmdb_id"])
            for r in recs:
                if r["tmdb_id"] not in existing_ids:
                    candidates.append(r)

    if len(candidates) < 5:
        genres = await get_watched_genres()
        if genres:
            genre_recs = await discover_by_genres(genres)
            for r in genre_recs:
                if r["tmdb_id"] not in existing_ids:
                    candidates.append(r)

    seen_ids: set[int] = set()
    unique: list[dict] = []
    for c in candidates:
        if c["tmdb_id"] not in seen_ids:
            seen_ids.add(c["tmdb_id"])
            unique.append(c)

    random.shuffle(unique)
    picks = unique[:5]

    if not picks:
        await update.message.reply_text(
            "Не удалось найти рекомендации 😔 Попробуй добавить ещё фильмов в список."
        )
        return

    context.user_data["rec_picks"] = picks

    for i, movie in enumerate(picks):
        kp_id, kp_rating = await get_kp_rating(movie["title"], movie.get("year"))
        movie["kp_id"] = kp_id
        movie["kp_rating"] = kp_rating

        year_str = f"({movie['year']})" if movie.get("year") else ""
        rating_str = f"⭐ КП: {kp_rating:.1f}" if kp_rating else "рейтинг не найден"
        overview = movie.get("overview") or "Описание недоступно."
        genres = movie.get("genres") or "—"
        text = (
            f"🎬 <b>{movie['title']}</b> {year_str}\n"
            f"Жанры: {genres}\n"
            f"{rating_str}\n\n"
            f"{overview}"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Добавить в список", callback_data=f"rec_add:{i}")]
        ])

        if movie.get("poster_url"):
            await update.message.reply_photo(
                photo=movie["poster_url"],
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


async def rec_add_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    idx = int(query.data.split(":")[1])
    picks = context.user_data.get("rec_picks", [])
    if idx >= len(picks):
        await query.answer("Что-то пошло не так.", show_alert=True)
        return

    movie = picks[idx]
    added = await add_movie(
        title=movie["title"],
        year=movie.get("year"),
        tmdb_id=movie["tmdb_id"],
        kp_id=movie.get("kp_id"),
        genres=movie.get("genres", ""),
        kp_rating=movie.get("kp_rating"),
        poster_url=movie.get("poster_url"),
    )

    if added:
        await query.answer(f"✅ «{movie['title']}» добавлен в список!", show_alert=True)
    else:
        await query.answer(f"Этот фильм уже есть в твоём списке.", show_alert=True)
