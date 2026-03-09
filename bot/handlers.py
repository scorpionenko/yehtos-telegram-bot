from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.queue_manager import add_request, get_request
from bot.queue_manager import get_random_request
from bot.rating_manager import add_rating, get_average_rating

router = Router()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="😔 Попросити підтримку")],
        [KeyboardButton(text="🤝 Допомогти комусь")],
        [KeyboardButton(text="👤 Мій профіль")]
    ],
    resize_keyboard=True
)

support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Написати підтримку", callback_data="write_support")],
        [InlineKeyboardButton(text="🔄 Інший запит", callback_data="next_request")]
    ]
)

rating_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐1", callback_data="rate_1"),
            InlineKeyboardButton(text="⭐2", callback_data="rate_2"),
            InlineKeyboardButton(text="⭐3", callback_data="rate_3"),
            InlineKeyboardButton(text="⭐4", callback_data="rate_4"),
            InlineKeyboardButton(text="⭐5", callback_data="rate_5"),
        ]
    ]
)

waiting_for_problem = set()
answering_request = {}
rating_targets = {}

@router.message(Command("start"))
async def start(message: types.Message):

    await message.answer(
        "👋 Привіт!\n\n"
        "Я бот «ЄХтось».\n\n"
        "Іноді всім нам потрібна підтримка.",
        reply_markup=menu
    )


@router.message()
async def handle_message(message: types.Message):

    user_id = message.from_user.id
    text = message.text.strip()

    print("MESSAGE:", text)

    # --------------------
    # кнопка підтримки
    # --------------------

    if "Попросити підтримку" in text:

        waiting_for_problem.add(user_id)

        await message.answer(
            "Опиши свою проблему.\n"
            "Твоє повідомлення буде передане іншій людині."
        )

        return

    # --------------------
    # користувач пише проблему
    # --------------------

    if user_id in waiting_for_problem:

        add_request(user_id, text)

        waiting_for_problem.remove(user_id)

        await message.answer(
            "Дякую ❤️\n"
            "Вашу проблему додано у список запитів."
        )

        return


    # --------------------
    # нова логіка допомоги
    # --------------------

    if "Допомогти комусь" in text:

        request = get_random_request()

        if request is None:

            await message.answer("Зараз немає активних запитів.")

            return

        answering_request[user_id] = request["user_id"]

        await message.answer(
            f"Людина просить підтримки:\n\n{request['text']}",
            reply_markup=support_keyboard
        )

        return


    # --------------------
    # написання підтримки
    # --------------------

    if user_id in answering_request:

        receiver = answering_request[user_id]

        await message.bot.send_message(
            receiver,
            f"💬 Вам надіслали підтримку:\n\n{text}"
        )

        await message.answer("Ваше повідомлення надіслано ❤️")

        rating_targets[receiver] = user_id

        await message.bot.send_message(
            receiver,
            "Оцініть допомогу:",
            reply_markup=rating_keyboard
        )

        del answering_request[user_id]

        return


    # --------------------
    # профіль
    # --------------------

    if "Мій профіль" in text:

        rating = get_average_rating(user_id)

        await message.answer(
            f"Ваш рейтинг допомоги: ⭐ {rating}"
        )


@router.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):

    user_id = callback.from_user.id

    if callback.data == "next_request":

        request = get_random_request()

        if request is None:

            await callback.message.answer("Більше запитів немає.")

            return

        answering_request[user_id] = request["user_id"]

        await callback.message.edit_text(
            f"Людина просить підтримки:\n\n{request['text']}",
            reply_markup=support_keyboard
        )


    if callback.data == "write_support":

        await callback.message.answer(
            "Напиши повідомлення підтримки."
        )


    # --------------------
    # оцінка
    # --------------------

    if callback.data.startswith("rate_"):

        score = int(callback.data.split("_")[1])

        helper_id = rating_targets.get(user_id)

        if helper_id:

            add_rating(helper_id, score)

            await callback.message.answer(
                "Дякуємо за оцінку ❤️"
            )

            del rating_targets[user_id]