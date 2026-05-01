import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from config import TELEGRAM_TOKEN
from database.db import init_db
from handlers.start import start, MAIN_MENU
from handlers.my_list import show_list, list_callback
from handlers.add_movie import add_movie_start, handle_title_input, pick_movie_callback, WAITING_TITLE
from handlers.mark_watched import show_unwatched, mark_watched_callback
from handlers.recommend import show_recommendations, rec_add_callback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def post_init(application):
    await init_db()


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    add_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Добавить фильм$"), add_movie_start)],
        states={
            WAITING_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title_input)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(add_conv)
    app.add_handler(MessageHandler(filters.Regex("^📋 Мой список$"), show_list))
    app.add_handler(MessageHandler(filters.Regex("^🎲 Рекомендации$"), show_recommendations))
    app.add_handler(MessageHandler(filters.Regex("^✅ Отметить просмотренным$"), show_unwatched))
    app.add_handler(CallbackQueryHandler(list_callback, pattern=r"^list:"))
    app.add_handler(CallbackQueryHandler(pick_movie_callback, pattern=r"^add_pick:"))
    app.add_handler(CallbackQueryHandler(mark_watched_callback, pattern=r"^watched:"))
    app.add_handler(CallbackQueryHandler(rec_add_callback, pattern=r"^rec_add:"))

    print("Бот запущен. Нажми Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
