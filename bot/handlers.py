from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.queue_manager import add_request, get_request
from bot.queue_manager import get_random_request
from bot.rating_manager import add_rating, get_average_rating
from bot.user_service import create_user
from aiogram import F

router = Router()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="😔 Попросити підтримку")],
        [KeyboardButton(text="🤝 Допомогти комусь")],
        [KeyboardButton(text="👤 Мій профіль")],
        [KeyboardButton(text="👨‍⚕️ Стати психологом")]
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

waiting_for_certificate = set()
waiting_for_problem = set()
answering_request = {}
rating_targets = {}

def admin_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Прийняти",
                    callback_data=f"approve_{user_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Відхилити",
                    callback_data=f"reject_{user_id}"
                )
            ]
        ]
    )

@router.message(Command("start"))
async def start(message: types.Message):

    await create_user(
        user_id=message.from_user.id,
        username=message.from_user.username
    )

    await message.answer(
        "👋 Привіт!\n\n"
        "Я бот «ЄХтось».\n\n"
        "Іноді всім нам потрібна підтримка.",
        reply_markup=menu
    )


from aiogram import F

@router.message(F.text)
async def handle_message(message: types.Message):

    user_id = message.from_user.id

    if not message.text:
        return
    
    text = message.text.strip()
    
    print("MESSAGE:", text)

    # --------------------
    # кнопка підтримки
    # --------------------
     
    if user_id in waiting_for_certificate:
        await message.answer("Ти вже відправив заявку ⏳")
        return 
      
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

    if "Стати психологом" in text:
    
        waiting_for_certificate.add(user_id)
    
        await message.answer(
            "Надішліть фото або PDF сертифіката 📄"
        )
    
        return
    # --------------------
    # профіль
    # --------------------

    if "Мій профіль" in text:

        rating = get_average_rating(user_id)

        await message.answer(
            f"Ваш рейтинг допомоги: ⭐ {rating}"
        )


@router.callback_query(F.data.in_(["next_request", "write_support"]) | F.data.startswith("rate_"))
async def handle_callbacks(callback: types.CallbackQuery):

    await callback.answer()
    
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


from aiogram import F

@router.message(F.photo | F.document)
async def handle_certificate(message: types.Message):

    user_id = message.from_user.id

    if user_id not in waiting_for_certificate:
        return

    file_id = (
        message.document.file_id
        if message.document
        else message.photo[-1].file_id
    )

    waiting_for_certificate.remove(user_id)

    await message.answer("Заявку відправлено адміну ✅")

    ADMIN_ID = 846605249

    await message.bot.send_message(
        ADMIN_ID,
        f"Нова заявка на психолога від {user_id}"
    )

    if message.document:
        await message.bot.send_document(
            ADMIN_ID,
            file_id,
            reply_markup=admin_keyboard(user_id)
            )
    else:
        await message.bot.send_photo(
            ADMIN_ID,
            file_id,
            reply_markup=admin_keyboard(user_id)
         )

@router.message(Command("approve"))
async def approve_user(message: types.Message):

    if message.from_user.id != 846605249:
        return

    try:
        user_id = int(message.text.split()[1])
    except:
        await message.answer("Формат: /approve user_id")
        return

    from bot.user_service import set_role, set_verified

    await set_role(user_id, "psychologist")
    await set_verified(user_id, True)

    await message.answer("Користувача підтверджено ✅")

    await message.bot.send_message(
        user_id,
        "Вас підтверджено як психолога 👨‍⚕️"
    )                

@router.callback_query(F.data.startswith("approve_"))
async def approve_callback(callback: types.CallbackQuery):

    user_id = int(callback.data.split("_")[1])

    from bot.user_service import set_role, set_verified

    await set_role(user_id, "psychologist")
    await set_verified(user_id, True)

    await callback.message.answer("Користувача підтверджено ✅")

    await callback.bot.send_message(
        user_id,
        "Вас підтверджено як психолога 👨‍⚕️"
    )


@router.callback_query(F.data.startswith("reject_"))
async def reject_callback(callback: types.CallbackQuery):

    user_id = int(callback.data.split("_")[1])

    await callback.message.answer("Заявку відхилено ❌")

    await callback.bot.send_message(
        user_id,
        "Вашу заявку відхилено ❌"
    )        