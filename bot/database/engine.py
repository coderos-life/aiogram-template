from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.database.models.custom_funcs import all_functions
from bot.database.repos import Repositories
from bot.enums.db import Databases
from bot.settings import settings

logger = logging.getLogger("Database")

URL = settings.db.build_postgres_url() if settings.db.used == Databases.PostgreSQL else settings.db.build_mysql_url()


engine = create_async_engine(
    URL,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
    pool_timeout=settings.db.pool_timeout,
    pool_recycle=settings.db.pool_recycle,
    echo=settings.debug_mode,
)
sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@asynccontextmanager
async def get_repo() -> AsyncGenerator[Repositories, None]:
    async with sessionmaker() as s:
        logger.debug("session was create")
        try:
            yield Repositories.get_repo(s)
        except Exception:
            await s.rollback()
            raise


async def create_database_custom_functions() -> None:
    async with sessionmaker() as s:
        async with s.begin():
            for func in all_functions:
                await s.execute(func)

    logger.debug("all database functions was installed")
