from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="😔 Попросити підтримку")],
        [KeyboardButton(text="🤝 Допомогти комусь")],
        [KeyboardButton(text="👤 Мій профіль")]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привіт!\n\n"
        "Я бот **«ЄХтось»**.\n\n"
        "Іноді всім нам потрібна підтримка.\n"
        "Тут ти можеш анонімно поговорити з людиною, "
        "яка готова вислухати.\n\n"
        "Обери дію нижче 👇",
        reply_markup=menu
    )
@router.message(Command("help"))
async def help(message: types.Message):
    await message.answer(
        "Як працює бот:\n\n"
        "😔 Попросити підтримку — напиши про свою проблему\n"
        "🤝 Допомогти комусь — підтримай іншу людину\n"
        "👤 Мій профіль — твій рейтинг та статистика"
    )
@router.message()
async def handle_message(message: types.Message):

    if message.text == "😔 Попросити підтримку":
        await message.answer(
            "Опиши свою проблему.\n"
            "Твоє повідомлення буде передане іншій людині анонімно."
        )

    elif message.text == "🤝 Допомогти комусь":
        await message.answer(
            "Зараз немає активних запитів."
        )

    elif message.text == "👤 Мій профіль":
        await message.answer(
            "Тут буде твій рейтинг і статистика."
        )