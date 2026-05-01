from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from services.tmdb import search_movies
from services.kinopoisk import get_kp_rating
from database.queries import add_movie
from handlers.start import MAIN_MENU

WAITING_TITLE = 1


async def add_movie_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши название фильма, который хочешь добавить:",
        reply_markup=MAIN_MENU,
    )
    return WAITING_TITLE


async def handle_title_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text.strip()
    await update.message.reply_text(f"🔍 Ищу «{query_text}»...")

    results = await search_movies(query_text)
    if not results:
        await update.message.reply_text(
            "Ничего не нашёл 😔 Попробуй другое название.",
            reply_markup=MAIN_MENU,
        )
        return ConversationHandler.END

    context.user_data["search_results"] = results

    buttons = []
    for i, movie in enumerate(results):
        year = movie.get("year") or "?"
        label = f"{movie['title']} ({year})"
        buttons.append([InlineKeyboardButton(label, callback_data=f"add_pick:{i}")])
    buttons.append([InlineKeyboardButton("❌ Отмена", callback_data="add_pick:cancel")])

    await update.message.reply_text(
        "Выбери нужный фильм:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return ConversationHandler.END


async def pick_movie_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_pick:cancel":
        await query.edit_message_text("Добавление отменено.")
        return

    idx = int(query.data.split(":")[1])
    results = context.user_data.get("search_results", [])
    if idx >= len(results):
        await query.edit_message_text("Что-то пошло не так. Попробуй снова.")
        return

    movie = results[idx]
    await query.edit_message_text(f"⏳ Добавляю «{movie['title']}», подтягиваю рейтинг КП...")

    kp_id, kp_rating = await get_kp_rating(movie["title"], movie.get("year"))

    added = await add_movie(
        title=movie["title"],
        year=movie.get("year"),
        tmdb_id=movie["tmdb_id"],
        kp_id=kp_id,
        genres=movie.get("genres", ""),
        kp_rating=kp_rating,
        poster_url=movie.get("poster_url"),
    )

    year_str = f"({movie['year']})" if movie.get("year") else ""
    rating_str = f"⭐ {kp_rating}" if kp_rating else "рейтинг не найден"
    if added:
        await query.edit_message_text(
            f"✅ Добавлено: {movie['title']} {year_str}\n"
            f"Жанры: {movie.get('genres', '—')}\n"
            f"КП: {rating_str}"
        )
    else:
        await query.edit_message_text(
            f"Фильм «{movie['title']}» уже есть в твоём списке."
        )
