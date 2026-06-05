import aiosqlite
from database.main_DB import data_base


# ─── Начало смены ─────────────────────────────────────────────────────────────

async def db_start_work(user_id: int, name: str, start_time: str):
    async with aiosqlite.connect(data_base) as db:
        await db.execute(
            """INSERT INTO work (user_id, name, start_time) VALUES (?, ?, ?)""",
            (user_id, name, start_time),
        )
        await db.commit()


# ─── Поиск активной смены ─────────────────────────────────────────────────────

async def db_get_active_shift(user_id: int):
    async with aiosqlite.connect(data_base) as db:
        async with db.execute(
            """SELECT id, start_time FROM work
               WHERE user_id = ? AND end_time IS NULL
               ORDER BY id DESC LIMIT 1""",
            (user_id,),
        ) as cursor:
            return await cursor.fetchone()


# ─── Завершение смены ─────────────────────────────────────────────────────────

async def db_end_work(work_id: int, end_time: str, hours: float, many: float):
    async with aiosqlite.connect(data_base) as db:
        await db.execute(
            """UPDATE work SET end_time = ?, hours = ?, many = ? WHERE id = ?""",
            (end_time, hours, many, work_id),
        )
        await db.commit()


# ─── Статистика пользователя ──────────────────────────────────────────────────

async def db_get_user_records(user_id: int):
    async with aiosqlite.connect(data_base) as db:
        async with db.execute(
            """SELECT * FROM work WHERE user_id = ?""", (user_id,)
        ) as cursor:
            return await cursor.fetchall()


# ─── Все пользователи ─────────────────────────────────────────────────────────

async def db_get_all_users():
    async with aiosqlite.connect(data_base) as db:
        async with db.execute(
            """SELECT DISTINCT user_id, name FROM work"""
        ) as cursor:
            return await cursor.fetchall()


# ─── Существует ли пользователь ───────────────────────────────────────────────

async def db_user_exists(user_id: int):
    async with aiosqlite.connect(data_base) as db:
        async with db.execute(
            """SELECT name FROM work WHERE user_id = ?""", (user_id,)
        ) as cursor:
            return await cursor.fetchall()


# ─── Удаление пользователя ────────────────────────────────────────────────────

async def db_delete_user(user_id: int):
    async with aiosqlite.connect(data_base) as db:
        await db.execute("""DELETE FROM work WHERE user_id = ?""", (user_id,))
        await db.commit()


# ─── Полная очистка базы ──────────────────────────────────────────────────────

async def db_clear_all():
    async with aiosqlite.connect(data_base) as db:
        await db.execute("DELETE FROM work")
        await db.execute("DROP TABLE IF EXISTS work")
        await db.execute("""CREATE TABLE IF NOT EXISTS work (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            start_time TEXT,
            end_time TEXT,
            hours REAL,
            many REAL,
            workout_date TEXT DEFAULT (DATETIME('now', 'localtime'))
        )""")
        await db.commit()


# ─── Добавить часы вручную (админ) ────────────────────────────────────────────

async def db_add_hours(user_id: int, name: str, hours: float):
    """Создаём завершённую запись вручную, start/end помечаем как ручное добавление"""
    many = round(hours * 400, 2)
    async with aiosqlite.connect(data_base) as db:
        await db.execute(
            """INSERT INTO work (user_id, name, start_time, end_time, hours, many)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, name, "ручное добавление", "ручное добавление", hours, many),
        )
        await db.commit()
    return many


# ─── Убрать часы (админ) ──────────────────────────────────────────────────────

async def db_remove_hours(user_id: int, hours_to_remove: float):
    """
    Удаляем часы из последних завершённых смен пользователя (от новых к старым).
    Возвращает (removed, debt) — сколько реально убрали и остаток если часов не хватило.
    """
    async with aiosqlite.connect(data_base) as db:
        async with db.execute(
            """SELECT id, hours FROM work
               WHERE user_id = ? AND hours IS NOT NULL
               ORDER BY id DESC""",
            (user_id,),
        ) as cursor:
            records = await cursor.fetchall()

        remaining = hours_to_remove
        total_removed = 0.0

        for record_id, record_hours in records:
            if remaining <= 0:
                break

            record_hours = record_hours or 0.0

            if record_hours <= remaining:
                # Убираем всю смену целиком
                remaining -= record_hours
                total_removed += record_hours
                new_hours = 0.0
            else:
                # Убираем часть из смены
                new_hours = round(record_hours - remaining, 2)
                total_removed += remaining
                remaining = 0.0

            new_many = round(new_hours * 400, 2)
            await db.execute(
                """UPDATE work SET hours = ?, many = ? WHERE id = ?""",
                (new_hours, new_many, record_id),
            )

        await db.commit()

    total_removed = round(total_removed, 2)
    debt = round(remaining, 2)  # сколько не смогли убрать — часов не хватило
    return total_removed, debt
