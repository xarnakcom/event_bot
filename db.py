# инициализация базы данных
import aiosqlite

DB_NAME = "Заменить_имя_базы_данных_бота.db"  # например "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            name TEXT,
            role TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_time TEXT,
            meet_place TEXT,
            customer TEXT,
            work_address TEXT,
            city TEXT,
            region TEXT,
            foreman_id INTEGER,
            weather TEXT,
            tools TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS event_workers (
            event_id INTEGER,
            worker_id INTEGER
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS worker_responses (
            event_id INTEGER,
            worker_id INTEGER,
            response TEXT
        )
        """)
        await db.commit()
