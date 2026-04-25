from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_keyboard = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="@coderos", url="https://t.me/coderos"),
            InlineKeyboardButton(text="Template", url="https://github.com/coderos-life/aiogram-bot-template"),
        ]
    ]
).as_markup()
