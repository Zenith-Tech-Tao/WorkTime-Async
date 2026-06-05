from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def buton_main_Inline():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Начать работу", callback_data="start"),
                InlineKeyboardButton(text="Закончить работу", callback_data="end"),
            ],
            [InlineKeyboardButton(text="Статистика", callback_data="stats")],
        ]
    )
    return keyboard


def end_work():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Закончить работу", callback_data="end")]
        ]
    )
    return keyboard


def menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
        ]
    )
    return keyboard


def stats_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Моя статистика", callback_data="me_stats"),
                InlineKeyboardButton(text="Общая статистика", callback_data="global_stats"),
            ]
        ]
    )
    return keyboard


def clear_DB_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, очистить", callback_data="clear_yes"),
                InlineKeyboardButton(text="❌ Нет, отмена", callback_data="clear_no"),
            ]
        ]
    )
    return keyboard


def cancel_dell():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="dell_no")]
        ]
    )
    return keyboard


def confirm_remove_user(user_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"remove_yes_{user_id}"),
                InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_remove"),
            ]
        ]
    )
    return keyboard
