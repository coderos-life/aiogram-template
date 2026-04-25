from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base_models import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
