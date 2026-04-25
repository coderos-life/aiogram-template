from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base_models import Base


class Chat(Base):
    __tablename__ = "chats"
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
