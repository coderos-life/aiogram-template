from __future__ import annotations

from aiogram.types import Chat as AiogramChat

from bot.database.models import Chat

from .base import BaseRepo


class ChatsRepo(BaseRepo[Chat]):
    model = Chat

    async def create_from_aiogram_model(self, chat: AiogramChat) -> Chat:
        return await self.create(id=chat.id, title=chat.title)
