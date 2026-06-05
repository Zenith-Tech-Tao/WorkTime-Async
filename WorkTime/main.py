import asyncio
import sys
import os

# Добавляем корень проекта в путь, чтобы импорты работали
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TOKEN
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database.main_DB import db_init
from routes.command import bot as command_router
from routes.work import bot as work_router
from routes.handlers_STATS import bot as stats_router
from routes.handlers_ADMIN import bot as admin_router

dp = Dispatcher(storage=MemoryStorage())

# Подключаем все роутеры
dp.include_router(command_router)
dp.include_router(work_router)
dp.include_router(stats_router)
dp.include_router(admin_router)


async def main():
    try:
        await db_init()

        bot = Bot(token=TOKEN)
        print("Скрипт для бота запущен!")
        await dp.start_polling(bot)

    except Exception as e:
        print("Произошла непредвиденная ошибка!\n")
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Описание: {e}")


if __name__ == "__main__":
    asyncio.run(main())
