from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database.queries import get_all_movies, mark_as_watched


async def show_unwatched(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = await get_all_movies(watched=0)
    if not movies:
        await update.message.reply_text(
            "Нет непросмотренных фильмов в списке. Сначала добавь что-нибудь через ➕ Добавить фильм"
        )
        return

    buttons = []
    for movie in movies:
        year = f"({movie['year']})" if movie.get("year") else ""
        rating = f" ⭐{movie['kp_rating']}" if movie.get("kp_rating") else ""
        label = f"{movie['title']} {year}{rating}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"watched:{movie['id']}")])

    await update.message.reply_text(
        "Выбери фильм, который ты посмотрел:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def mark_watched_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    movie_id = int(query.data.split(":")[1])

    movies = await get_all_movies(watched=0)
    movie = next((m for m in movies if m["id"] == movie_id), None)

    await mark_as_watched(movie_id)

    title = movie["title"] if movie else "Фильм"
    await query.edit_message_text(f"✅ «{title}» отмечен как просмотренный!")
