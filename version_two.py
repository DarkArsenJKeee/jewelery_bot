import asyncio
from collections import defaultdict

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

# ================== НАСТРОЙКИ ==================


import os
from aiogram import Bot, Dispatcher

TOKEN = os.getenv("BOT_TOKEN")  # вернёт строку
bot = Bot(TOKEN)
dp = Dispatcher()

# пути к картинкам (ЛОКАЛЬНЫЕ файлы)
IMAGES = {
    "star": ["img/star1.jpg", "img/star2.jpg", "img/star3.jpg", "img/star4.jpg"],
    "fire": ["img/fire1.jpg", "img/fire2.jpg", "img/fire3.jpg", "img/fire4.jpg"],
    "shield": ["img/shield1.jpg", "img/shield2.jpg", "img/shield3.jpg", "img/shield4.jpg"],
    "heart": ["img/heart1.jpg", "img/heart2.jpg", "img/heart3.jpg", "img/heart4.jpg"],
}

# ================== ДАННЫЕ ТЕСТА ==================

QUESTIONS = [
    {
        "num": "1️⃣",
        "text": "Как ты входишь в этот год?",
        "answers": [
            ("🛡 Спокойно и осознанно", "shield"),
            ("🤍 С чувством перемен", "heart"),
            ("🔥 Через внутренний вызов", "fire"),
            ("⭐️ С надеждой и ожиданием", "star"),
        ],
    },
    {
        "num": "2️⃣",
        "text": "Что для тебя сейчас важнее всего?",
        "answers": [
            ("🛡 Защита и границы", "shield"),
            ("🔥 Рост и развитие", "fire"),
            ("🤍 Любовь и близость", "heart"),
            ("⭐️ Ясность и направление", "star"),
        ],
    },
    {
        "num": "3️⃣",
        "text": "Что ты чаще выбираешь?",
        "answers": [
            ("⭐️ Интуицию", "star"),
            ("🔥 Действие", "fire"),
            ("🤍 Принятие", "heart"),
            ("🛡 Наблюдение", "shield"),
        ],
    },
    {
        "num": "4️⃣",
        "text": "Какой образ откликается сильнее?",
        "answers": [
            ("🤍 Свет", "heart"),
            ("🛡 Круг", "shield"),
            ("🔥 Пламя", "fire"),
            ("⭐️ Путь", "star"),
        ],
    },
]

RESULT_TEXT = {
    "star": (
        "🌟 **Твой символ года — Звезда**\n\n"
        "Год ориентира и внутреннего света.\n"
        "Даже если путь не до конца ясен — ты уже движешься в верном направлении.\n\n"
        "💫 Украшение со звездой — напоминание о надежде, вере в себя и своём пути.\n\n"
        "_Твой символ — не случайность._"
    ),
    "fire": (
        "🔥 **Твой символ года — Огонь**\n\n"
        "Год силы и трансформации.\n"
        "Про смелость, честные решения и отказ от того, что больше не твоё.\n\n"
        "🐦‍🔥 Украшение с этим символом — якорь твоей внутренней энергии.\n\n"
        "_Твой символ — не случайность._"
    ),
    "shield": (
        "🛡 **Твой символ года — Щит / Оберег**\n\n"
        "Год устойчивости и заботы о себе.\n"
        "Про границы, безопасность и опору внутри.\n\n"
        "✨ Украшение-оберег — тихое напоминание, что ты под защитой.\n\n"
        "_Твой символ — не случайность._"
    ),
    "heart": (
        "🤍 **Твой символ года — Сердце**\n\n"
        "Год чувств, близости и искренности.\n"
        "Про честность с собой и тёплые связи.\n\n"
        "💗 Украшение с этим символом — напоминание жить из сердца.\n\n"
        "_Твой символ — не случайность._"
    ),
}

# ================== БОТ ==================

bot = Bot(TOKEN)
dp = Dispatcher()

user_progress = {}
user_scores = defaultdict(lambda: defaultdict(int))

# ================== КЛАВИАТУРЫ ==================

def start_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✨ Начать тест", callback_data="start_test")]
        ]
    )

def question_kb(q_index: int, chosen: str | None = None):
    buttons = []
    for text, symbol in QUESTIONS[q_index]["answers"]:
        label = text
        if chosen == symbol:
            label += " ✅"
        buttons.append(
            [InlineKeyboardButton(
                text=label,
                callback_data=f"answer:{q_index}:{symbol}"
            )]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================== ХЕНДЛЕРЫ ==================

@dp.message(Command("start"))


async def start(message: Message):
    user_progress[message.from_user.id] = 0
    user_scores[message.from_user.id].clear()

    await message.answer(
        "✨ Привет. Этот короткий тест поможет определить твой личный символ года — "
        "образ, который будет поддерживать тебя и напоминать о важном.\n\n"
        "Ответь интуитивно, здесь нет «правильных» вариантов.",
        reply_markup=start_kb(),
    )

@dp.callback_query(F.data == "start_test")
async def begin_test(call: CallbackQuery):
    await call.answer()
    await send_question(call.from_user.id)

@dp.callback_query(F.data.startswith("answer:"))
async def answer_handler(call: CallbackQuery):
    _, q_index, symbol = call.data.split(":")
    q_index = int(q_index)

    user_scores[call.from_user.id][symbol] += 1

    # подсветка выбранного варианта
    await call.message.edit_reply_markup(
        reply_markup=question_kb(q_index, chosen=symbol)
    )

    user_progress[call.from_user.id] += 1

    await call.answer()

    if user_progress[call.from_user.id] < len(QUESTIONS):
        await send_question(call.from_user.id)
    else:
        await send_result(call.from_user.id)

# ================== ЛОГИКА ==================

async def send_question(user_id: int):
    q = QUESTIONS[user_progress[user_id]]
    await bot.send_message(
        user_id,
        f"{q['num']} **{q['text']}**",
        reply_markup=question_kb(user_progress[user_id]),
        parse_mode="Markdown",
    )

from aiogram.types import InputMediaPhoto
from aiogram.types import FSInputFile

async def send_result(user_id: int):
    scores = user_scores[user_id]
    result = max(scores, key=scores.get)

    media = []

    for img_path in IMAGES[result]:
        media.append(
            InputMediaPhoto(
                media=FSInputFile(img_path)
            )
        )

    # 1️⃣ Отправляем 4 картинки одним блоком
    await bot.send_media_group(
        chat_id=user_id,
        media=media
    )

    # 2️⃣ Отправляем текст ОТДЕЛЬНЫМ сообщением ниже
    await bot.send_message(
        chat_id=user_id,
        text=RESULT_TEXT[result],
        parse_mode="Markdown"
    )
    # 3️⃣ Финальное тёплое сообщение
    await bot.send_message(
        chat_id=user_id,
        text=(
            "✨ Благодарим вас за внимание и доверие.\n\n"
            "Иногда один символ может сказать больше слов.\n"
            "Оставайтесь с нами — впереди новые смыслы и красивые перемены."
        )
    )


# ================== ЗАПУСК ==================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())