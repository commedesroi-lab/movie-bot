from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["📋 Мой список", "➕ Добавить фильм"],
        ["🎲 Рекомендации", "✅ Отметить просмотренным"],
    ],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я твой личный помощник по фильмам 🎬\n\n"
        "Здесь ты можешь вести список фильмов, отмечать просмотренные "
        "и получать персональные рекомендации.\n\n"
        "Выбери действие:",
        reply_markup=MAIN_MENU,
    )
