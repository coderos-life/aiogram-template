from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, InlineQuery, Message, TelegramObject

from bot.settings import settings


class IsAdmin(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        if isinstance(event, Message) and event.from_user:
            user = event.from_user.id

        elif isinstance(event, CallbackQuery):
            user = event.from_user.id

        elif isinstance(event, InlineQuery) and event.from_user:
            user = event.from_user.id
        else:
            user = None

        if not user:
            return False

        return user in settings.admins
