# хендлеры для администратора (создание, статус)
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from db import DB_NAME
import aiosqlite
from weather import get_weather

router = Router()

# Заменить список ID админов на свои Telegram ID
ADMINS = [Заменить_список_Telegram_ID_админов_целыми_числами]  # пример: [123456789, 987654321]

class EventCreation(StatesGroup):
    datetime = State()
    meet_place = State()
    customer = State()
    work_address = State()
    foreman = State()
    workers = State()

@router.message(F.text == "/create_event")
async def start_create(msg: Message, state: FSMContext):
    if msg.from_user.id not in ADMINS:
        return await msg.answer("У вас нет прав администратора.")
    await state.set_state(EventCreation.datetime)
    await msg.answer("Введите дату и время (например: 10.10.2025 12:00):")

@router.message(EventCreation.datetime)
async def get_datetime(msg: Message, state: FSMContext):
    await state.update_data(datetime=msg.text)
    await state.set_state(EventCreation.meet_place)
    await msg.answer("Введите место встречи (Улица, Город):")

@router.message(EventCreation.meet_place)
async def get_meet_place(msg: Message, state: FSMContext):
    await state.update_data(meet_place=msg.text)
    await state.set_state(EventCreation.customer)
    await msg.answer("Введите имя заказчика:")

@router.message(EventCreation.customer)
async def get_customer(msg: Message, state: FSMContext):
    await state.update_data(customer=msg.text)
    await state.set_state(EventCreation.work_address)
    await msg.answer("Введите адрес объекта (Улица, Город, Область):")

@router.message(EventCreation.work_address)
async def get_work_address(msg: Message, state: FSMContext):
    parts = msg.text.split(',')
    if len(parts) < 3:
        return await msg.answer("Формат: Улица, Город, Область")
    city = parts[1].strip()
    region = parts[2].strip()
    await state.update_data(work_address=msg.text, city=city, region=region)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT tg_id, name FROM users WHERE role = 'foreman'")
        foremen = await cursor.fetchall()

    if not foremen:
        return await msg.answer("Нет зарегистрированных бригадиров.")

    buttons = "\n".join([f"{f[0]} - {f[1]}" for f in foremen])
    await state.set_state(EventCreation.foreman)
    await msg.answer("Выберите бригадира (введите его TG ID):\n" + buttons)

@router.message(EventCreation.foreman)
async def get_foreman(msg: Message, state: FSMContext):
    try:
        foreman_id = int(msg.text)
        await state.update_data(foreman=foreman_id)
    except:
        return await msg.answer("Введите TG ID цифрами.")

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT tg_id, name FROM users WHERE role = 'worker'")
        workers = await cursor.fetchall()

    if not workers:
        return await msg.answer("Нет зарегистрированных рабочих.")

    buttons = "\n".join([f"{w[0]} - {w[1]}" for w in workers])
    await state.set_state(EventCreation.workers)
    await msg.answer("Выберите рабочих (через пробел, TG ID):\n" + buttons)

@router.message(EventCreation.workers)
async def finalize_event(msg: Message, state: FSMContext, bot=types.Bot):
    try:
        worker_ids = list(map(int, msg.text.strip().split()))
    except:
        return await msg.answer("Введите TG ID через пробел.")

    data = await state.get_data()
    weather = await get_weather(data["city"])

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO events (date_time, meet_place, customer, work_address, city, region, foreman_id, weather)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["datetime"],
            data["meet_place"],
            data["customer"],
            data["work_address"],
            data["city"],
            data["region"],
            data["foreman"],
            weather
        ))
        event_id = cursor.lastrowid

        for worker_id in worker_ids:
            await db.execute("INSERT INTO event_workers (event_id, worker_id) VALUES (?, ?)", (event_id, worker_id))
        await db.commit()

    foreman_text = f"""
<b>{data["datetime"]}</b>
Заказчик: {data["customer"]}
Объект: {data["work_address"]}
Место встречи: {data["meet_place"]}
Бригадир: @{msg.from_user.username or msg.from_user.full_name}
Рабочие: {' '.join(map(str, worker_ids))}
Погода: {weather}
"""
    await bot.send_message(data["foreman"], foreman_text)
    await bot.send_message(data["foreman"], "Какие инструменты и материалы нужно взять с собой? Напишите сообщением.")

    await msg.answer("Событие создано и отправлено бригадиру ✅")
    await state.clear()

from aiogram.filters import Command

@router.message(Command("status"))
async def check_status(msg: Message):
    if msg.from_user.id not in ADMINS:
        return await msg.answer("У вас нет прав администратора.")

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT id, date_time, customer, work_address 
            FROM events 
            ORDER BY id DESC LIMIT 1
        """)
        event = await cursor.fetchone()
        if not event:
            return await msg.answer("Событий не найдено.")

        event_id, dt, customer, address = event

        cursor = await db.execute("""
            SELECT u.name, u.tg_id
            FROM users u
            JOIN event_workers ew ON u.tg_id = ew.worker_id
            WHERE ew.event_id = ?
        """, (event_id,))
        workers = await cursor.fetchall()

        cursor = await db.execute("""
            SELECT worker_id, response
            FROM worker_responses
            WHERE event_id = ?
        """, (event_id,))
        responses_raw = await cursor.fetchall()
        responses = {r[0]: r[1] for r in responses_raw}

    lines = [f"<b>Статус события:</b>\n{dt}\nОбъект: {address}\nЗаказчик: {customer}\n\n<b>Отклики рабочих:</b>"]

    for name, tg_id in workers:
        if tg_id in responses:
            icon = "✅" if responses[tg_id] == "yes" else "❌"
        else:
            icon = "❓"
        lines.append(f"{icon} {name} (@{tg_id})")

    await msg.answer("\n".join(lines))
