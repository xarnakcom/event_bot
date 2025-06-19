# хендлеры для рабочих (отклики)
from aiogram import Router
from aiogram.types import CallbackQuery
import aiosqlite
from db import DB_NAME

router = Router()

@router.callback_query(lambda c: c.data.startswith("confirm_"))
async def handle_response(callback: CallbackQuery):
    user_id = callback.from_user.id
    response = "yes" if callback.data == "confirm_yes" else "no"

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT e.id
            FROM events e
            JOIN event_workers ew ON e.id = ew.event_id
            WHERE ew.worker_id = ? 
            ORDER BY e.id DESC LIMIT 1
        """, (user_id,))
        result = await cursor.fetchone()

        if not result:
            await callback.answer("Событие не найдено.")
            return

        event_id = result[0]

        cursor = await db.execute("""
            SELECT response FROM worker_responses
            WHERE event_id = ? AND worker_id = ?
        """, (event_id, user_id))
        already = await cursor.fetchone()

        if already:
            await callback.answer("Вы уже ответили.")
            return

        await db.execute("""
            INSERT INTO worker_responses (event_id, worker_id, response)
            VALUES (?, ?, ?)
        """, (event_id, user_id, response))
        await db.commit()

    await callback.message.edit_reply_markup()  # Убирает кнопки
    await callback.answer("Ответ получен, спасибо!")
