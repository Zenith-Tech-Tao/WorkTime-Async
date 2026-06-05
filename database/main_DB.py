import aiosqlite

data_base = "data_base.db"


async def db_init():
    async with aiosqlite.connect(data_base) as db:
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
