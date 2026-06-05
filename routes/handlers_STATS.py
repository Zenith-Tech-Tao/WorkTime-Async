'''Подсчет и введение статистики пользователя

Статистика (stats, me_stats, global_stats)

'''

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.script_DB import db_get_user_records, db_get_all_users
from routes.keyboards import stats_menu

bot = Router()


# === МЕНЮ СТАТИСТИКИ ===
@bot.callback_query(F.data == "stats")
async def cb_stats(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "Выбери подходящую статистику:",
            reply_markup=stats_menu(),
        )

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await callback.answer()


# === МОЯ СТАТИСТИКА ===
@bot.callback_query(F.data == "me_stats")
async def cb_me_stats(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        name = callback.from_user.username or callback.from_user.first_name

        # Получаем ВСЕ записи пользователя из базы
        all_records = await db_get_user_records(user_id)

        # Инициализируем счётчики
        summa_sessions = 0
        summa_hors = 0.0
        summa_money = 0.0

        # Считаем статистику вручную
        for record in all_records:
            # record[5] = hours, record[6] = many
            if record[5] is not None:  # Если есть часы — сессия завершена
                summa_sessions += 1
                summa_hors += round(record[5] or 0, 2)
                summa_money += round(record[6] or 0, 2)

        # Округляем итоговые значения
        summa_hors = round(summa_hors, 2)
        summa_money = round(summa_money, 2)

        # Формируем сообщение в зависимости от наличия данных
        if summa_sessions > 0:
            message_text = (
                f"Статистика пользователя: <b>{name}</b>\n\n"
                f"📅 Всего: {summa_hors:.2f} часов\n"
                f"💰 Заработано: {summa_money:.2f} руб\n\n"
                f"📋 Всего рабочих сессий: {summa_sessions}\n"
                f"💵 Ставка: 400 руб./час"
            )
        else:
            message_text = (
                f"📊 Статистика пользователя: {name}\n\n"
                f"📅 Всего: 0 часов\n"
                f"💰 Заработано: 0 руб\n\n"
                f"📋 Всего рабочих сессий: 0\n"
                f"💵 Ставка: 400 руб./час"
            )

        await callback.message.edit_text(message_text, parse_mode="HTML")

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await callback.answer()


# === ОБЩАЯ СТАТИСТИКА ===
@bot.callback_query(F.data == "global_stats")
async def cb_global_stats(callback: CallbackQuery):
    try:
        # Получаем уникальных пользователей из базы
        all_users = await db_get_all_users()

        if not all_users:
            await callback.message.edit_text(
                "📊 <b>Общая статистика:</b>\n\nНет данных о пользователях",
                parse_mode="HTML",
            )
            await callback.answer()
            return

        message_info = "📊 <b>Общая статистика:</b>\n\n"

        # Для каждого пользователя считаем статистику отдельно
        for user_id, user_name in all_users:
            user_records = await db_get_user_records(user_id)

            summa_sessions = 0
            summa_hors = 0.0
            summa_money = 0.0

            for record in user_records:
                if record[5] is not None:
                    summa_sessions += 1
                    summa_hors += round(record[5] or 0, 2)
                    summa_money += round(record[6] or 0, 2)

            summa_hors = round(summa_hors, 2)
            summa_money = round(summa_money, 2)

            message_info += (
                f"👤 <b>{user_name}</b>:\n"
                f"   📅 Всего: {summa_hors:.2f} ч.\n"
                f"   💰 Зарплата: {summa_money:.2f} руб.\n"
                f"   📋 Всего рабочих сессий: {summa_sessions}\n"
                f"   💵 Ставка: 400 руб./час\n\n"
            )

        await callback.message.edit_text(message_info, parse_mode="HTML")

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await callback.answer()
