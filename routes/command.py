'''Здесь описываем разные команды'''

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from routes.keyboards import buton_main_Inline

bot = Router()


# -------------СТАРТ--------------#

@bot.message(Command("start"))
async def start(message: Message):
    try:
        id_user = message.from_user.id
        # Получаем имя пользователя: сначала username, если нет - first_name
        name = message.from_user.username or message.from_user.first_name
        await message.answer(
            f"Здравствуйте, <b>{name}</b>.👋 \n\n"
            f"Это бот для счета отработанных часов и зарплаты.\n\n"
            f"Выберите действие:",
            reply_markup=buton_main_Inline(),
            parse_mode="HTML",
        )

        print(
            f"\nid: {id_user} - @{name}; Команда: /start\n"
            "Данные пользователя обновлены!"
        )

    except Exception as e:
        print("Произошла непредвиденная ошибка!\n")
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Описание: {e}")
