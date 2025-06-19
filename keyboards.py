# клавиатуры с кнопками
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
     InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")]
])
