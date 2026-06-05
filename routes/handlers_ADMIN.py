'''Здесь описываем команды Админа

Команды:
  /db          — очистить всю базу
  /du          — удалить пользователя
  /add_hours   — добавить часы пользователю вручную
  /rem_hours   — убрать часы у пользователя
'''

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from WorkTime.config import Admin_id
from database.script_DB import (
    db_get_all_users,
    db_get_user_records,
    db_user_exists,
    db_delete_user,
    db_clear_all,
    db_add_hours,
    db_remove_hours,
)
from routes.keyboards import clear_DB_menu, cancel_dell, confirm_remove_user

bot = Router()


# ─── FSM состояния ────────────────────────────────────────────────────────────

class DeleteUserState(StatesGroup):
    waiting_for_user_id = State()

class AddHoursState(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_hours   = State()

class RemoveHoursState(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_hours   = State()


# ─── Вспомогательная функция: список пользователей ───────────────────────────

async def build_users_list() -> str:
    """Формирует текст со списком всех пользователей и их статистикой"""
    all_users = await db_get_all_users()

    if not all_users:
        return None

    text = "📋 <b>Список пользователей:</b>\n\n"

    for user_id, user_name in all_users:
        records = await db_get_user_records(user_id)

        sessions = 0
        total_hours = 0.0
        total_money = 0.0

        for record in records:
            if record[5] is not None:
                sessions += 1
                total_hours += round(record[5] or 0, 2)
                total_money += round(record[6] or 0, 2)

        text += (
            f"👤 <b>{user_name}</b>\n"
            f"   🔢 ID: <code>{user_id}</code>\n"
            f"   📊 Сессий: {sessions}\n"
            f"   ⏱️ Часов: {round(total_hours, 2):.2f}\n"
            f"   💰 Заработано: {round(total_money, 2):.2f} руб.\n\n"
        )

    return text


# ═══════════════════════════════════════════════════════════════════════════════
# /db — очистка всей базы данных
# ═══════════════════════════════════════════════════════════════════════════════

@bot.message(Command("db"))
async def cmd_clear_db(message: Message):
    try:
        if message.from_user.id != Admin_id:
            await message.reply("⛔ У вас нет прав для этой команды!")
            return

        await message.reply(
            "⚠️ <b>Внимание! Вы собираетесь удалить ВСЕ данные из базы.</b>\n\n"
            "Это действие нельзя отменить!\n\n"
            "Вы уверены?",
            reply_markup=clear_DB_menu(),
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")


@bot.callback_query(F.data == "clear_yes")
async def cb_clear_yes(callback: CallbackQuery):
    try:
        await db_clear_all()
        await callback.message.edit_text(
            "✅ <b>База данных полностью очищена!</b> Все данные удалены.",
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")
    await callback.answer()


@bot.callback_query(F.data == "clear_no")
async def cb_clear_no(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "❌ <b>Очистка базы данных отменена.</b>",
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")
    await callback.answer()


# ═══════════════════════════════════════════════════════════════════════════════
# /du — удаление конкретного пользователя
# ═══════════════════════════════════════════════════════════════════════════════

@bot.message(Command("du"))
async def cmd_dell_user(message: Message, state: FSMContext):
    try:
        if message.from_user.id != Admin_id:
            await message.reply("⛔ У вас нет прав для этой команды!")
            return

        text = await build_users_list()

        if not text:
            await message.reply(
                "📊 <b>Общая статистика:</b>\n\nНет данных о пользователях",
                parse_mode="HTML",
            )
            return

        text += "\n👇 <b>Введите ID пользователя для удаления:</b>"

        await message.reply(text, parse_mode="HTML", reply_markup=cancel_dell())
        await state.set_state(DeleteUserState.waiting_for_user_id)

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")


@bot.message(DeleteUserState.waiting_for_user_id)
async def process_dell_user_id(message: Message, state: FSMContext):
    try:
        if message.from_user.id != Admin_id:
            await state.clear()
            return

        id_text = message.text.strip()

        if not id_text.isdigit():
            await message.reply("❌ ID должен быть числом!\nПопробуйте снова: /du")
            await state.clear()
            return

        user_id = int(id_text)
        user_exists = await db_user_exists(user_id)

        if user_exists:
            user_name = user_exists[0][0] if user_exists[0][0] else "Без имени"
            await message.answer(
                f"⚠️ <b>Подтвердите удаление:</b>\n\n"
                f"👤 Имя: {user_name}\n"
                f"🔢 ID: {id_text}\n\n"
                f"Удалить этого пользователя?",
                reply_markup=confirm_remove_user(user_id),
                parse_mode="HTML",
            )
        else:
            await message.answer(
                f"❌ Пользователь с ID {id_text} не найден.\n"
                f"Попробуйте снова: /du"
            )

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await state.clear()


@bot.callback_query(F.data == "dell_no")
async def cb_dell_no(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await callback.message.edit_text("❌ <b>Действие отменено.</b>", parse_mode="HTML")
    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")
    await callback.answer()


@bot.callback_query(F.data.startswith("remove_yes_"))
async def cb_remove_yes(callback: CallbackQuery):
    try:
        user_id = int(callback.data.split("_")[2])
        await db_delete_user(user_id)
        await callback.message.edit_text(
            f"✅ <b>Пользователь удален!</b>\n\n"
            f"ID: {user_id}\n"
            f"Все данные удалены из базы.",
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")
    await callback.answer()


@bot.callback_query(F.data == "cancel_remove")
async def cb_cancel_remove(callback: CallbackQuery):
    try:
        await callback.message.edit_text("❌ <b>Удаление отменено.</b>", parse_mode="HTML")
    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")
    await callback.answer()


# ═══════════════════════════════════════════════════════════════════════════════
# /add_hours — добавить часы пользователю вручную
# ═══════════════════════════════════════════════════════════════════════════════

@bot.message(Command("add_hours"))
async def cmd_add_hours(message: Message, state: FSMContext):
    try:
        if message.from_user.id != Admin_id:
            await message.reply("⛔ У вас нет прав для этой команды!")
            return

        text = await build_users_list()

        if not text:
            await message.reply(
                "📊 Нет данных о пользователях.\n"
                "Сначала пользователь должен хотя бы раз нажать /start.",
                parse_mode="HTML",
            )
            return

        text += "\n👇 <b>Введите ID пользователя, которому добавить часы:</b>"

        await message.reply(text, parse_mode="HTML", reply_markup=cancel_dell())
        await state.set_state(AddHoursState.waiting_for_user_id)

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")


@bot.message(AddHoursState.waiting_for_user_id)
async def process_add_hours_user_id(message: Message, state: FSMContext):
    try:
        if message.from_user.id != Admin_id:
            await state.clear()
            return

        id_text = message.text.strip()

        if not id_text.isdigit():
            await message.reply("❌ ID должен быть числом!\nПопробуйте снова: /add_hours")
            await state.clear()
            return

        user_id = int(id_text)
        user_exists = await db_user_exists(user_id)

        if not user_exists:
            await message.reply(
                f"❌ Пользователь с ID {id_text} не найден.\n"
                f"Попробуйте снова: /add_hours"
            )
            await state.clear()
            return

        user_name = user_exists[0][0] if user_exists[0][0] else "Без имени"

        # Сохраняем данные пользователя в FSM и переходим к вводу часов
        await state.update_data(user_id=user_id, user_name=user_name)
        await state.set_state(AddHoursState.waiting_for_hours)

        await message.answer(
            f"👤 Пользователь: <b>{user_name}</b>\n"
            f"🔢 ID: <code>{user_id}</code>\n\n"
            f"⏱️ <b>Сколько часов добавить?</b>\n"
            f"Введите число (можно дробное, например: 3.5)",
            parse_mode="HTML",
        )

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")


@bot.message(AddHoursState.waiting_for_hours)
async def process_add_hours_amount(message: Message, state: FSMContext):
    try:
        if message.from_user.id != Admin_id:
            await state.clear()
            return

        hours_text = message.text.strip().replace(",", ".")

        try:
            hours = float(hours_text)
            if hours <= 0:
                raise ValueError
        except ValueError:
            await message.reply(
                "❌ Введите корректное положительное число!\n"
                "Например: 4 или 3.5"
            )
            await state.clear()
            return

        data = await state.get_data()
        user_id = data["user_id"]
        user_name = data["user_name"]

        many = await db_add_hours(user_id, user_name, hours)

        await message.answer(
            f"✅ <b>Часы успешно добавлены!</b>\n\n"
            f"👤 Пользователь: <b>{user_name}</b>\n"
            f"🔢 ID: <code>{user_id}</code>\n"
            f"⏱️ Добавлено часов: <b>{hours}</b>\n"
            f"💰 Начислено: <b>{many} руб.</b>",
            parse_mode="HTML",
        )

        print(f"Админ добавил {hours} ч. пользователю {user_name} (id: {user_id})")

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await state.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# /rem_hours — убрать часы у пользователя
# ═══════════════════════════════════════════════════════════════════════════════

@bot.message(Command("rem_hours"))
async def cmd_rem_hours(message: Message, state: FSMContext):
    try:
        if message.from_user.id != Admin_id:
            await message.reply("⛔ У вас нет прав для этой команды!")
            return

        text = await build_users_list()

        if not text:
            await message.reply(
                "📊 Нет данных о пользователях.",
                parse_mode="HTML",
            )
            return

        text += "\n👇 <b>Введите ID пользователя, у которого убрать часы:</b>"

        await message.reply(text, parse_mode="HTML", reply_markup=cancel_dell())
        await state.set_state(RemoveHoursState.waiting_for_user_id)

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")


@bot.message(RemoveHoursState.waiting_for_user_id)
async def process_rem_hours_user_id(message: Message, state: FSMContext):
    try:
        if message.from_user.id != Admin_id:
            await state.clear()
            return

        id_text = message.text.strip()

        if not id_text.isdigit():
            await message.reply("❌ ID должен быть числом!\nПопробуйте снова: /rem_hours")
            await state.clear()
            return

        user_id = int(id_text)
        user_exists = await db_user_exists(user_id)

        if not user_exists:
            await message.reply(
                f"❌ Пользователь с ID {id_text} не найден.\n"
                f"Попробуйте снова: /rem_hours"
            )
            await state.clear()
            return

        user_name = user_exists[0][0] if user_exists[0][0] else "Без имени"

        # Считаем сколько часов у пользователя всего
        records = await db_get_user_records(user_id)
        total_hours = sum(round(r[5] or 0, 2) for r in records if r[5] is not None)

        await state.update_data(user_id=user_id, user_name=user_name)
        await state.set_state(RemoveHoursState.waiting_for_hours)

        await message.answer(
            f"👤 Пользователь: <b>{user_name}</b>\n"
            f"🔢 ID: <code>{user_id}</code>\n"
            f"⏱️ Всего часов: <b>{round(total_hours, 2)}</b>\n\n"
            f"✂️ <b>Сколько часов убрать?</b>\n"
            f"Введите число (можно дробное, например: 2.5)",
            parse_mode="HTML",
        )

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")


@bot.message(RemoveHoursState.waiting_for_hours)
async def process_rem_hours_amount(message: Message, state: FSMContext):
    try:
        if message.from_user.id != Admin_id:
            await state.clear()
            return

        hours_text = message.text.strip().replace(",", ".")

        try:
            hours = float(hours_text)
            if hours <= 0:
                raise ValueError
        except ValueError:
            await message.reply(
                "❌ Введите корректное положительное число!\n"
                "Например: 4 или 2.5"
            )
            await state.clear()
            return

        data = await state.get_data()
        user_id = data["user_id"]
        user_name = data["user_name"]

        removed, debt = await db_remove_hours(user_id, hours)
        money_removed = round(removed * 400, 2)

        if debt > 0:
            # Часов не хватило — убрали меньше чем просили
            await message.answer(
                f"⚠️ <b>Часы убраны частично!</b>\n\n"
                f"👤 Пользователь: <b>{user_name}</b>\n"
                f"🔢 ID: <code>{user_id}</code>\n"
                f"✂️ Убрано часов: <b>{removed}</b>\n"
                f"💸 Списано: <b>{money_removed} руб.</b>\n\n"
                f"⚠️ Не хватило ещё <b>{debt} ч.</b> — у пользователя закончились записи.",
                parse_mode="HTML",
            )
        else:
            await message.answer(
                f"✅ <b>Часы успешно убраны!</b>\n\n"
                f"👤 Пользователь: <b>{user_name}</b>\n"
                f"🔢 ID: <code>{user_id}</code>\n"
                f"✂️ Убрано часов: <b>{removed}</b>\n"
                f"💸 Списано: <b>{money_removed} руб.</b>",
                parse_mode="HTML",
            )

        print(f"Админ убрал {removed} ч. у пользователя {user_name} (id: {user_id})")

    except Exception as e:
        print(f"Тип ошибки: {type(e).__name__}\nОписание: {e}")

    await state.clear()
