# хендлеры для бригадира (инструменты)
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db import DB_NAME
import aiosqlite
from keyboards import confirm_kb

router = Router()

class ToolInput(StatesGroup):
    waiting_for_tools = State()

@router.message(commands=["tools"])
async def cmd_tools_start(msg: types.Message, state: FSMContext):
    await state.set_state(ToolInput.waiting_for_tools)
    await msg.answer("Напишите, какие инструменты и материалы нужно взять с собой:")

@router.message(ToolInput.waiting_for_tools)
async def handle_tools(msg: types.Message, state: FSMContext, bot=types.Bot):
    tools = msg.text
    user_id = msg.from_user.id

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT id, date_time, customer, work_address, meet_place, weather 
            FROM events 
            WHERE foreman_id = ? AND tools IS NULL 
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        event = await cursor.fetchone()

        if not event:
            return await msg.answer("Не найдено активных событий для подтверждения инструментов.")

        event_id, dt, customer, work_addr, meet, weather = event

        await db.execute("UPDATE events SET tools = ? WHERE id = ?", (tools, event_id))
        await db.commit()

        cursor = await db.execute("""
            SELECT u.tg_id 
            FROM users u
            JOIN event_workers ew ON u.tg_id = ew.worker_id
            WHERE ew.event_id = ?
        """, (event_id,))
        workers = await cursor.fetchall()

    text = f"""
<b>{dt}</b>
Заказчик: {customer}
Объект: {work_addr}
Место встречи: {meet}
Бригадир: @{msg.from_user.username or msg.from_user.full_name}
Погода: {weather}
Комментарий бригадира: {tools}
"""

    for (tg_id,) in workers:
        await bot.send_message(tg_id, text.strip())
        await bot.send_message(tg_id, "Вы будете?", reply_markup=confirm_kb)

    await msg.answer("Комментарий добавлен, рабочим отправлены уведомления ✅")
    await state.clear()
