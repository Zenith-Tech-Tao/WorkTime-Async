from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime

from database.script_DB import (
    db_start_work,
    db_get_active_shift,
    db_end_work,
)
from routes.keyboards import end_work, menu, buton_main_Inline

bot = Router()


# === НАЧАТЬ РАБОТУ ===
@bot.callback_query(F.data == "start")
async def cb_start_work(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        name = callback.from_user.username or callback.from_user.first_name
        # Текущее время в формате "день-месяц-год, час:минута"
        start_time = datetime.now().strftime("%d-%m-%Y, %H:%M")

        # Сохраняем начало работы в базу данных
        await db_start_work(user_id, name, start_time)

        await callback.message.edit_text(
            f"✅ <b>Работа начата!</b>\n\n"
            f"🕐 {start_time}\n\n"
            f"Не забудь нажать 'Закончить' когда закончите!",
            parse_mode="HTML",
            reply_markup=end_work(),
        )

        print(f"id: {user_id} - @{name}; Начал работу в {start_time}")

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await callback.answer()


# === ЗАКОНЧИТЬ РАБОТУ ===
@bot.callback_query(F.data == "end")
async def cb_end_work(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        name = callback.from_user.username or callback.from_user.first_name
        end_time = datetime.now()

        # Ищем последнюю незавершённую смену пользователя
        last_work = await db_get_active_shift(user_id)

        if last_work:
            work_id, start_time_str = last_work

            # Преобразуем строку времени в объект datetime для расчётов
            start_time_obj = datetime.strptime(start_time_str, "%d-%m-%Y, %H:%M")

            # Вычисляем разницу во времени
            time_difference = end_time - start_time_obj

            # Переводим секунды в часы
            hours = round(time_difference.total_seconds() / 3600, 2)

            # Рассчитываем зарплату: 400 руб/час
            many = round(hours * 400, 2)
            end_time_str = end_time.strftime("%d-%m-%Y, %H:%M")

            # Обновляем запись в базе данных
            await db_end_work(work_id, end_time_str, hours, many)

            await callback.message.answer(
                f"✅ <b>Работа завершена</b> в {end_time_str}!\n\n"
                f"👤 Пользователь: <b>{name}</b>\n"
                f"⏱️ Отработано: {hours} часов\n"
                f"💰 Заработано: {many} руб.",
                reply_markup=menu(),
                parse_mode="HTML",
            )

            print(f"id: {user_id} - @{name}; Закончил работу в {end_time_str}. Часов: {hours}, Заработано: {many}")

        else:
            # Если нет активной смены
            await callback.message.answer(
                f"❌ <b>{name}</b>, у вас <b>нет активных смен!</b>\n"
                "Нажми 'Начать' чтобы начать новую.",
                parse_mode="HTML",
            )

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await callback.answer()


# === ГЛАВНОЕ МЕНЮ ===
@bot.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery):
    try:
        await callback.message.answer(
            "👷 <b>ГББ: Центр управления работой</b> 👷\n\n"
            '"<b>Начать</b>" — Начинает новую рабочую смену.\n'
            '"<b>Закончить</b>" — Завершает текущую активную смену.\n'
            '"<b>Статистика</b>" — Показывает вашу персональную или общую статистику.\n\n'
            "Выберите действия:",
            reply_markup=buton_main_Inline(),
            parse_mode="HTML",
        )

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await callback.answer()