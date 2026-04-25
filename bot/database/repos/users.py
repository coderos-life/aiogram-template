from __future__ import annotations

from typing import Any, Sequence

from aiogram.types import User as AiogramUser
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.database.models import User

from .base import BaseRepo


class UsersRepo(BaseRepo[User]):
    model = User

    async def create_from_aiogram_model(self, user: AiogramUser) -> User:
        return await self.create(id=user.id, username=user.username)

    async def get_by_user_id(self, user_id: int, *user_options: Any) -> User | None:
        q = select(User).where(User.id == user_id).options(*[selectinload(i) for i in user_options])

        return (await self.session.execute(q)).scalar()

    async def get_users_by_username(self, username: str) -> Sequence[User]:
        q = select(User).where(User.username == username)

        return (await self.session.execute(q)).scalars().all()
