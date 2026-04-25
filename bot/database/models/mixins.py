from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

if TYPE_CHECKING:
    from .user_models import User


class ReprMixin:
    _repr_max_length: ClassVar[int] = 25
    _repr_attrs: ClassVar[tuple[str, ...]] = ()

    def _repr_attrs_str(self) -> str:
        max_length = self._repr_max_length

        values: list[str] = []
        for key in self._repr_attrs:
            if not hasattr(self, key):
                msg = f"{self.__class__} has incorrect attribute '{key}' in _repr_attrs_"
                raise KeyError(msg)
            value = getattr(self, key)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."
            values.append("{}={}".format(key, value))

        return " ".join(values)

    def __repr__(self) -> str:
        attrs = self._repr_attrs_str()
        return f"<{self.__class__.__name__} {attrs}>" if attrs else f"<{self.__class__.__name__}>"


class SerializeMixin:
    def to_dict(self, ignored_columns: list[str] | None = None, relationships: bool = False) -> dict[str, Any]:
        if ignored_columns is None:
            ignored_columns = []
        result: dict[str, Any] = {}

        table = getattr(self, "__table__")
        mapper = getattr(self, "__mapper__")

        for c in table.columns:
            if c.name in ignored_columns:
                continue
            result[c.name] = getattr(self, c.name)

        if relationships:
            for relationship_name in mapper.relationships.keys():
                try:
                    relationship_value = getattr(self, relationship_name)
                except Exception:
                    continue

                if isinstance(relationship_value, list):
                    result[relationship_name] = [item.to_dict() for item in relationship_value]
                else:
                    result[relationship_name] = relationship_value.to_dict() if relationship_value is not None else None
        return result


class DateTimeMixin:
    _datetime_func: ClassVar[Any] = func.now()
    _datetime_timezone: ClassVar[bool] = False

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=cls._datetime_timezone),
            server_default=cls._datetime_func,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=cls._datetime_timezone), server_onupdate=cls._datetime_func)


class UserRelationshipMixin:
    _user_id_nullable: ClassVar[bool] = False
    _user_id_unique: ClassVar[bool] = False
    _user_back_populates: ClassVar[str | None] = None
    _user_relationship_kwargs: ClassVar[dict[str, Any]] = {}

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(BigInteger, ForeignKey("users.id"), unique=cls._user_id_unique, nullable=cls._user_id_nullable)

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship("User", back_populates=cls._user_back_populates, **cls._user_relationship_kwargs)
