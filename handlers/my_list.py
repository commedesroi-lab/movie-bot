from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from database.queries import get_all_movies

PAGE_SIZE = 10


def _format_movie(movie: dict) -> str:
    rating = f"⭐ {movie['kp_rating']}" if movie.get("kp_rating") else ""
    year = f"({movie['year']})" if movie.get("year") else ""
    title = movie["title"]
    if movie["watched"]:
        return f"✅ {title} {year} {rating}"
    return f"🎬 {title} {year} {rating}"


def _build_keyboard(page: int, total: int, filter_mode: str) -> InlineKeyboardMarkup:
    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ Назад", callback_data=f"list:{filter_mode}:{page - 1}"))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(InlineKeyboardButton("Вперёд ▶", callback_data=f"list:{filter_mode}:{page + 1}"))
    if nav:
        buttons.append(nav)

    filter_buttons = []
    if filter_mode != "all":
        filter_buttons.append(InlineKeyboardButton("📋 Все", callback_data="list:all:0"))
    if filter_mode != "unwatched":
        filter_buttons.append(InlineKeyboardButton("🎬 Непросмотренные", callback_data="list:unwatched:0"))
    if filter_mode != "watched":
        filter_buttons.append(InlineKeyboardButton("✅ Просмотренные", callback_data="list:watched:0"))
    if filter_buttons:
        buttons.append(filter_buttons)

    return InlineKeyboardMarkup(buttons)


async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _render_list(update, context, filter_mode="all", page=0, edit=False)


async def list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, filter_mode, page_str = query.data.split(":")
    await _render_list(update, context, filter_mode=filter_mode, page=int(page_str), edit=True)


async def _render_list(update: Update, context: ContextTypes.DEFAULT_TYPE,
                       filter_mode: str, page: int, edit: bool):
    watched_filter = None if filter_mode == "all" else (1 if filter_mode == "watched" else 0)
    movies = await get_all_movies(watched=watched_filter)

    if not movies:
        text = "Твой список пуст. Добавь первый фильм через ➕ Добавить фильм"
        if edit:
            await update.callback_query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    start = page * PAGE_SIZE
    chunk = movies[start: start + PAGE_SIZE]
    lines = [_format_movie(m) for m in chunk]
    header = {"all": "📋 Все фильмы", "watched": "✅ Просмотренные", "unwatched": "🎬 Непросмотренные"}[filter_mode]
    text = f"{header} ({len(movies)}):\n\n" + "\n".join(lines)

    keyboard = _build_keyboard(page, len(movies), filter_mode)
    if edit:
        await update.callback_query.edit_message_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)
