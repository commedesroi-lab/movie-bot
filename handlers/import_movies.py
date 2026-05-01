from telegram import Update
from telegram.ext import ContextTypes
from services.tmdb import search_movies
from services.kinopoisk import get_kp_rating
from database.queries import add_movie
import asyncio

WATCHED = [
    "Беспринципные", "007 Казино Рояль", "Предел риска", "Шоу Трумана",
    "Повар на колёсах", "Драйв", "Бегущий по лезвию 2049",
    "Пеле рождение легенды", "Волк с Уолл-стрит", "Бойцовский клуб",
    "Air большой прыжок", "Вольт", "Человек-паук", "Жизнь по вызову",
    "Остров проклятых", "Начало", "Тёмные воды", "Запах женщины",
    "Переводчик", "Бэтмен", "Сумерки", "Мег монстр глубины",
    "Игра в кальмара", "Форсаж", "Престиж", "Тор",
    "Американский психопат", "Всегда говори да", "Дюна", "Рататуй",
    "Исходный код", "Мотылёк", "Железный человек", "Фантастический мистер Фокс",
    "Васаби", "Джек Ричер", "Побег из Шоушенка",
    "Знакомьтесь Джо Блэк", "Отель Гранд Будапешт",
    "Невероятная жизнь Уолтера Митти", "Человек который изменил всё",
    "Черная пантера Ваканда навеки", "Укрощение строптивого",
]

UNWATCHED = [
    "Мюнхен", "Парфюмер", "Трасса 60", "Волшебная страна",
    "Игра престолов", "Баллада о Бастере Скраггсе", "Близнецы",
    "Линкольн для адвоката", "Три метра над уровнем неба", "ВАЛЛ-И",
    "Тренер", "Ограды", "Капитан Фантастик", "Вторая жизнь Уве",
    "Зелёная миля", "Клан Сопрано", "Вивариум", "Вавилон",
    "Револьвер", "Последний самурай", "Хатико",
    "Планета обезьян", "Талантливый мистер Рипли",
    "Гадкий я 4", "Мой учитель осьминог", "Ирландец",
    "Гран Туризмо", "Эдди Орёл", "Выживший",
    "Мастер и Маргарита", "Сто лет тому вперёд",
    "Игра", "Час пик", "Остров собак", "Миа и белый лев",
    "Кто убил BlackBerry", "Берсерк", "Духлесс",
    "Валериан и город тысячи планет", "Дворецкий",
    "Нокдаун", "Территория", "Бригада",
]


async def import_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = len(WATCHED) + len(UNWATCHED)
    msg = await update.message.reply_text(
        f"⏳ Начинаю импорт {total} фильмов. Это займёт пару минут..."
    )

    added = 0
    skipped = 0
    failed = 0

    async def process(title: str, watched: int):
        nonlocal added, skipped, failed
        try:
            results = await search_movies(title)
            if not results:
                failed += 1
                return
            movie = results[0]
            kp_id, kp_rating = await get_kp_rating(movie["title"], movie.get("year"))
            ok = await add_movie(
                title=movie["title"],
                year=movie.get("year"),
                tmdb_id=movie["tmdb_id"],
                kp_id=kp_id,
                genres=movie.get("genres", ""),
                kp_rating=kp_rating,
                poster_url=movie.get("poster_url"),
                watched=watched,
            )
            if ok:
                added += 1
            else:
                skipped += 1
        except Exception:
            failed += 1

    count = 0
    for title in WATCHED:
        await process(title, watched=1)
        count += 1
        if count % 10 == 0:
            await msg.edit_text(f"⏳ Обрабатываю... {count}/{total}")
        await asyncio.sleep(0.3)

    for title in UNWATCHED:
        await process(title, watched=0)
        count += 1
        if count % 10 == 0:
            await msg.edit_text(f"⏳ Обрабатываю... {count}/{total}")
        await asyncio.sleep(0.3)

    await msg.edit_text(
        f"✅ Импорт завершён!\n\n"
        f"Добавлено: {added}\n"
        f"Уже было в списке: {skipped}\n"
        f"Не найдено: {failed}\n\n"
        f"Открой 📋 Мой список чтобы проверить."
    )
